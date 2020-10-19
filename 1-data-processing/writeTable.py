#   HELPER FUNCTIONS AND OBJECTS FOR POSTGRESQL MIGRATION

from pyspark.sql import SparkSession 
import sys

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
    .option("password", "cockroach") \
    .save(mode=saveMode)
