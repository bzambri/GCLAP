from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import functions
from pyspark.sql.functions import *
from pyspark.sql.types import *
from writeTable import writeTable
from zonalMean import zonal_mean
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
schema = StructType([StructField('level', DoubleType(), nullable=False),
                     StructField('latitude', DoubleType(), nullable=False),
                     StructField('date', DateType(), nullable=False),
                     StructField('u', DoubleType(), nullable=False),
                     StructField('v', DoubleType(), nullable=False),
                     StructField('t', DoubleType(), nullable=False),
                     StructField('z', DoubleType(), nullable=False),
                     StructField('o3', DoubleType(), nullable=False)])

for yr in range(1979,2020):
    for mon in range(1,13):

        #open the S3 file
        s3file = f's3a://{bucket}/{key}/{yr}-{mon:02d}.nc'
        print(f'Reading file {s3file}..................\n')
        remote_file_obj = fs_s3.open(s3file, mode='rb')

        #open as xarray and convert to Pandas df
        pdf = xr.open_dataset(remote_file_obj, engine='h5netcdf').to_dataframe()

        #explode the table and convert to Spark df
        data = pdf.reset_index(level=['level', 'latitude', 'longitude', 'time'])
        df = spark.createDataFrame(data, schema=schema)

        #repartition so the chunks are small enought to write
        df = df.repartition(3000)

        #compute the zonal mean
        zm = zonal_mean(df)     

        #write to CockroachDB; create table if it's the first month
        if yr == 1979 and mon == 1:
            writeTable(zm, 'zonal_means')
        else:
            writeTable(zm, 'zonal_means', "append")

spark.stop()
