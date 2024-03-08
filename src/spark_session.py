from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import pyspark.sql.functions as F

class CustomSparkSession:
    def __init__(self) -> None:
        self.spark = (SparkSession.builder
            .appName("RealtimeVotingMaster")
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1") #mvnRepo- Spark Kafka Structured->3.5.1
            .config("spark.jars", "/Users/.../pathtojarfile") # Postgresql driver https://jdbc.postgresql.org/download/ Java8
            .config("spark.sql.adaptive.enable", 'false') #disable adaptive query executions
            .getOrCreate()
        )
    def _create_spark_session(self):
        return self.spark
    
    def create_kafka_schema():
        return StructType([
                StructField("voter_id", StringType(), True),
                StructField("candidate_id", StringType(), True),
                StructField("voting_time", TimestampType(), True),
                StructField("voter_name", StringType(), True),
                StructField("party_affiliation", StringType(), True),
                StructField("biography", StringType(), True),
                StructField("campaign_platform", StringType(), True),
                StructField("photo_url", StringType(), True),
                StructField("candidate_name", StringType(), True),
                StructField("date_of_birth", StringType(), True),
                StructField("gender", StringType(), True),
                StructField("nationality", StringType(), True),
                StructField("registration_number", StringType(), True),
                StructField("address", StructType([
                    StructField("street", StringType(), True),
                    StructField("city", StringType(), True),
                    StructField("state", StringType(), True),
                    StructField("country", StringType(), True),
                    StructField("postcode", StringType(), True)
                ]), True),
                StructField("email", StringType(), True),
                StructField("phone_number", StringType(), True),
                StructField("cell_number", StringType(), True),
                StructField("picture", StringType(), True),
                StructField("registered_age", IntegerType(), True),
                StructField("vote", IntegerType(), True)
        ])
    def create_votes_df(spark_session, vote_schema):
        return (spark_session.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", "votes_topic") \
            .option("startingOffsets", "earliest") \
            .load() \
            .selectExpr("CAST(value AS STRING)") \
            .select(F.from_json(F.col("value"), vote_schema).alias("data")) \
            .select("data.*")
        )