import pyspark.sql.functions as F
from pyspark.sql.types import IntegerType, TimestampType


from src.spark_session import CustomSparkSession

if __name__ == "__main__":
    #İnitialize spark session
    spark_session = CustomSparkSession()._create_spark_session()

    vote_schema = CustomSparkSession().create_kafka_schema()
    votes_df = CustomSparkSession().create_votes_df(spark_session)

    #Pre-processing the data
    votes_df = votes_df.withColumn('voting_time', F.col('voting_time').cast(TimestampType()))\
                       .withColumn('vote', F.col('vote').cast(IntegerType()))
    
    enriched_votes_df = votes_df.withWatermark('voting_time', '1 minute')

    #Aggregate votes per candidate and turnout by location
    votes_per_candidate = enriched_votes_df.groupBy('candidate_id', 'candidate_name', 'party_affiliation', 'photo_url')\
                                            .agg(F.sum('vote').alias('total_votes'))
    
    turnout_by_location = enriched_votes_df.groupBy('address.state').count().alias('total_votes')

    votes_per_candidate_to_kafka = (votes_per_candidate.selectExpr('to_json(struct(*)) AS value')\
                                                        .writeStream.format('kafka')\
                                                        .option('kafka.bootstrap.servers', 'localhost:9092')\
                                                        .option('topic', 'aggregated_votes_per_candidate')\
                                                        .option('checkpointLocation', '<checkpoint1_path')\
                                                        .outputMode('update')\
                                                        .start()
                                                        )

    turnout_by_location_to_kafka = (turnout_by_location.selectExpr('to_json(struct(*)) AS value')\
                                                        .writeStream.format('kafka')\
                                                        .option('kafka.bootstrap.servers', 'localhost:9092')\
                                                        .option('topic', 'aggregated_turnout_by_location')\
                                                        .option('checkpointLocation', '<checkpoint2_path')\
                                                        .outputMode('update')\
                                                        .start()
                                                        )
    
    #Await termination for the streaming queries
    votes_per_candidate_to_kafka.awaitTermination()
    turnout_by_location_to_kafka.awaitTermination()