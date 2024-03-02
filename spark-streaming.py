from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType
import pyspark.sql.functions as F

from src.spark_session import CustomSparkSession

if __name__ == "__main__":
    #İnitialize spark session
    spark_session = CustomSparkSession()._create_spark_session()

    vote_schema = CustomSparkSession().create_kafka_schema()
    votes_df = CustomSparkSession().create_votes_df(spark_session)
