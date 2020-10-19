from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import functions
from pyspark.sql.functions import *
from pyspark.sql.types import *
from writeTable import writeTable
import xarray as xr
import numpy as np
import datetime
import os
import s3fs

import warnings
warnings.filterwarnings('ignore')

bucket = 'reanalysis-folders'
key = 'ERA5/pressure-levels

sc = SparkContext()
spark = SparkSession(sc)
fs_s3 = s3fs.S3FileSystem()

#define the table schema
schema = StructType([StructField('latitude', DoubleType(), nullable=False),
                     StructField('longitude', DoubleType(), nullable=False),
                     StructField('date', DateType(), nullable=False),
                     StructField('u10', DoubleType(), nullable=False),
                     StructField('v10', DoubleType(), nullable=False),
                     StructField('d2m', DoubleType(), nullable=False),
                     StructField('t2m', DoubleType(), nullable=False),
                     StructField('msl', DoubleType(), nullable=False),
                     StructField('sst', DoubleType(), nullable=False),
                     StructField('sp' , DoubleType(), nullable=False),
                     StructField('tp' , DoubleType(), nullable=False)])

for yr in range(1979,2020):
    for mon in range(1,13):

        #open the S3 file
        s3file = f's3a://{bucket}/{key}/{yr}-{mon:02d}.nc'
        print(f'Reading file {s3file}..................\n')
        remote_file_obj = fs_s3.open(s3file, mode='rb')

        #open as xarray and convert to Pandas df
        pdf = xr.open_dataset(remote_file_obj, engine='h5netcdf').to_dataframe()

        #explode the table and convert to Spark df
        data = pdf.reset_index(level=['latitude','longitude','time'])
        df = spark.createDataFrame(data, schema=schema)

        #repartition so the chunks are small enought to write
        df = df.repartition(3000)

        #write to CockroachDB; create table if it's the first month
        if yr == 1979 and mon == 1:
            writeTable(df, 'single_level')
        else:
            writeTable(df, 'single_level', "append")

spark.stop()
