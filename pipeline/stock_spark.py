from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, LongType

# Create Spark session
spark = SparkSession.builder \
    .appName("Kafka Stream Processing") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
    .getOrCreate()

# Define the schema for Kafka message
schema = StructType([
    StructField("symbol", StringType(), True),
    StructField("date", StringType(), True), 
    StructField("open", FloatType(), True),
    StructField("close", FloatType(), True),
    StructField("high", FloatType(), True),
    StructField("low", FloatType(), True),
    StructField("volume", LongType(), True)
])

# Define Kafka stream
kafka_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "stock-data") \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON data from the Kafka stream
json_stream = kafka_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") 

# Write stream to the console for debugging
query = json_stream.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()
