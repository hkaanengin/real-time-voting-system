from src.postgre_actions import PostgreActions
from confluent_kafka import Consumer, KafkaException, KafkaError, SerializingProducer
import simplejson as json
import random
from datetime import datetime
from main import delivery_report

conf = {
    'bootstrap.servers': 'localhost:9092'
}
consumer = Consumer(conf | {
            'group.id': 'voting-group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }
    )
producer = SerializingProducer(conf)

if __name__ == "__main__":
    conn = PostgreActions().get_conn()
    cur = PostgreActions().get_cur()

    cur.execute("""
         SELECT row_to_json(col)
                FROM(
                SELECT * FROM candidates
                ) col;
        """
    )
    candidates = [candidate[0] for candidate in cur.fetchall()]

    if len(candidates) == 0:
        raise Exception("No candidates found in the database")
    else:
        print(candidates)

    consumer.subscribe(['voters_topic'])
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            elif msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break
            else:
                voter = json.loads(msg.value().decode('utf-8'))
                chosen_candidate = random.choice(candidates)
                vote = voter | chosen_candidate | {
                    'voting_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    'vote': 1
                }
            try:
                print('User {} is voting for candidate: {}'.format(vote['voter_id'], vote['candidate_id']))
                print(vote)
                PostgreActions().insert_votes(vote)

                producer.produce(
                    'votes_topic',
                    key = vote['voter_id'],
                    value = json.dumps(vote),
                    on_delivery = delivery_report
                )
                producer.poll(0)
            except Exception as e:
                print(f'Error inserting votes into DB due to: {e}')
        else:
            print("loop breaked")
    except Exception as e:
        print(e)