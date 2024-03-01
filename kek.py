import psycopg2
import random
from src.postgre_actions import PostgreActions


conn = psycopg2.connect("host=localhost dbname=votingDB user=kekuser password=kekpwd")
cur = conn.cursor()

cur.execute("""
    SELECT * FROM voters limit 10
""")
candidates = cur.fetchall()

print(candidates)