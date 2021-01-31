from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.functions import *
from tableFunctions import *

sc = SparkContext()
spark = SparkSession(sc)

#start SparkSQL session
sqlContext = SQLContext(sc)

#read the file with its header
df = sqlContext.read.option("header",True).csv("*.csv")
#count the number of rows (it is 4820022)
df.count()

#count the unique values in recipient_name (it is 153449)
df.select('recipient_name').distinct().count()

#delete periods, commas, and spaces from recipient names
df = df.withColumn('recipient_name', regexp_replace('recipient_name', ' AND ', ''))
df = df.withColumn('recipient_name', regexp_replace('recipient_name', '&', ''))
df = df.withColumn('recipient_name', regexp_replace('recipient_name', '\.', ''))
df = df.withColumn('recipient_name', regexp_replace('recipient_name', ',', ''))
df = df.withColumn('recipient_name', regexp_replace('recipient_name', ' ', ''))

#count again (it is now 149582)
df.select('recipient_name').distinct().count()

#create a global temporary view to execute SQL commands
df.createGlobalTempView("gov_spend")


#compare domestic and foreign contracts
all_contracts = spark.sql("SELECT COUNT(*) as n_contracts, SUM(total_dollars_obligated) AS total_obligated \
                                         FROM global_temp.gov_spend")

domestic_contracts = spark.sql("SELECT COUNT(*) as n_contracts, SUM(total_dollars_obligated) AS total_obligated \
                                                    FROM global_temp.gov_spend \
                                                    WHERE country_of_product_or_service_origin LIKE 'UNITED STATES%'")

foreign_contracts = spark.sql("SELECT COUNT(*) as n_contracts, SUM(total_dollars_obligated) AS total_obligated \
                                                 FROM global_temp.gov_spend \
                                                 WHERE country_of_product_or_service_origin NOT LIKE 'UNITED STATES%'")

letter = spark.sql("SELECT recipient_name, recipient_parent_name \
                             FROM global_temp.gov_spend \
                             WHERE LEFT(recipient_name,1) = LEFT(recipient_parent_name,1)")
letter.show(truncate=False)

#properties for postgres write
mode = "overwrite"
url = "jdbc:postgresql://10.0.0.11:5432/postgres"
properties = {"user": "postgres","password": <password>,"driver": "org.postgresql.Driver"}

#write to postgres
df.write.jdbc(url=url, table = "gov_spend", mode=mode, properties=properties)

