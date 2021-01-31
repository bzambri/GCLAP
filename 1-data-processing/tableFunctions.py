#   FUNCTIONS FOR SPARK TO INTERACT WITH CDB

from pyspark.sql import SparkSession 
import sys

# function to read a table from cockroachDB
def readTable(tableName, var, minLat, maxLat, minLon, maxLon, minDate, maxDate, numPartitions):
    query = "(SELECT date, lat, lon, " + var + " from " + tableName + \
            "WHERE \
                (latitude BETWEEN " + minLat + " AND " + maxLat + ") AND \
                (longitude BETWEEN " + minLon + " AND " + maxLon + ") AND \
                (date BETWEEN " + minDate + " AND " + maxDate + "))"
    cluster   = 'jdbc:postgresql://10.2.11.27:26257/era5'
    # read the table from postgresql
    try: 
        table0 = spark.read \
        .format("jdbc") \
        .option("driver", "org.postgresql.Driver") \
        .option("url", cluster) \
        .option("dbtable", query) \
        .option("user", "brian") \
        .option("password", "<your-password>") \
        .option("partitionColumn", "date") \
        .option("numPartitions", numPartitions) \
        .load() \
        .cache()
    except: 
        print("There's an issue with the partition process.", file=sys.stdout) 
        
    print("There are " + str(table0.rdd.getNumPartitions()) + " partitions " + \
          "across " + str(table0.rdd.count()) + " rows.", file=sys.stdout) 

    return table0


# function to write a table to cockroachDB    
def writeTable(table0, tableName, saveMode="error"):
    # have to repartition the table b/c cockroachDB can't take too many rows
    # at a time, max is around 1000
    # https://forum.cockroachlabs.com/t/whats-the-best-way-to-do-bulk-insert/58
    cluster   = 'jdbc:postgresql://10.2.11.27:26257/era5'
    table0.write \
    .format("jdbc") \
    .option("driver", "org.postgresql.Driver") \
    .option("url", cluster) \
    .option("dbtable", tableName) \
    .option("user", "brian") \
    .option("password", "<your-password>") \
    .save(mode=saveMode)
