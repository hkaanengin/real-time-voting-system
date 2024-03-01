import psycopg2
import random
from src.postgre_actions import PostgreActions
from confluent_kafka import SerializingProducer
import json

PARTIES = ['AKP', 'CHP', 'MHP', 'Iyi Parti']
NUMBER_OF_VOTERS = 1000

random.seed(20)

def delivery_report(err, msg):
    if err is not None: 
        print(f"Message delivery failed due to: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

if __name__ == "__main__":
    producer = SerializingProducer({'bootstrap.servers': 'localhost:9092'})
    try:
        conn = PostgreActions().get_conn()
        cur = PostgreActions().get_cur()
        PostgreActions().postgre_create_tables()

        cur.execute("""
            SELECT * FROM candidates
        """)
        candidates = cur.fetchall()

        if len(candidates) == 0:
            for i in range(len(PARTIES)):  #refactor this part
                candidate = PostgreActions.populate_candidate_data(i, len(PARTIES))
                print(candidate)
                PostgreActions().insert_candidates(candidate)
        else:
            print("There are candidates present in the 'candidates' table")

        cur.execute("""
            SELECT * FROM voters
        """)
        voters = cur.fetchall()

        for i in range(NUMBER_OF_VOTERS-len(voters)):
            voter_data = PostgreActions.populate_voter_data()
            PostgreActions().insert_voters(voter_data)

            producer.produce(
                "voters_topic",
                key= voter_data['voter_id'],
                value = json.dumps(voter_data),
                on_delivery = delivery_report
            )

            print('Produced voter {}, data:{}'.format(i, voter_data))
            producer.flush()
    except Exception as e:
        print(f"Unable to create tables/connect to the postgre DB: {e}")