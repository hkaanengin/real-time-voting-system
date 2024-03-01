import psycopg2
import requests
from dotenv import load_dotenv
import os

DB_CREDENTIALS_ENV = ".\env-variables\.db-credentials.env"
BASE_URL = "https://randomuser.me/api/?nat=tr"
PARTIES = ['AKP', 'CHP', 'MHP', 'Iyi Parti']

class PostgreActions:
    def __init__(self) -> None:
        load_dotenv(DB_CREDENTIALS_ENV)
        self.conn = psycopg2.connect(f"host={os.getenv('host')} dbname={os.getenv('dbname')} user={os.getenv('user')} password={os.getenv('password')}")
        self.cur = self.conn.cursor()

    def get_conn(self):
        return self.conn

    def get_cur(self):
        return self.conn.cursor()

    def postgre_create_tables(self):
        self.cur.execute(
            """
                CREATE TABLE IF NOT EXISTS candidates (
                    candidate_id VARCHAR(255) PRIMARY KEY,
                    candidate_name VARCHAR(255),
                    party_affiliation VARCHAR(255),
                    biography TEXT,
                    campaign_platform TEXT,
                    photo_url TEXT
                )
            """
        )

        self.cur.execute(
            """
                CREATE TABLE IF NOT EXISTS voters (
                    voter_id VARCHAR(255) PRIMARY KEY,
                    voter_name VARCHAR(255),
                    date_of_birth DATE,
                    gender VARCHAR(255),
                    nationality VARCHAR(255),
                    registration_number VARCHAR(255),
                    address_street VARCHAR(255),
                    address_city VARCHAR(255),
                    address_state VARCHAR(255),
                    address_country VARCHAR(255),
                    address_postcode VARCHAR(255),
                    phone_number VARCHAR(255),
                    picture TEXT,
                    registered_age INTEGER
                )
            """
        )

        self.cur.execute(
            """
                CREATE TABLE IF NOT EXISTS votes (
                    voter_id VARCHAR(255) UNIQUE,
                    candidate_id VARCHAR(255),
                    voting_time TIMESTAMP,
                    vote INT DEFAULT 1,
                    PRIMARY KEY (voter_id, candidate_id)
                )
            """
        )

        self.conn.commit()

    def populate_candidate_data(candidate_number, total_parties):
        response = requests.get(BASE_URL+ '&gender=' + ('female' if candidate_number%2 ==1 else 'male'))
        if response.status_code == 200:
            candidate_data = response.json()['results'][0]

            return {
                'candidate_id': candidate_data['login']['uuid'],  #might wanna generate an independent uuid from uuid8
                'candidate_name': f"{candidate_data['name']['first']} {candidate_data['name']['last']}",
                'party_affiliation': PARTIES[candidate_number % total_parties],
                'biography': "A brief biography of candidate",
                'campaign_platform': "Key campaign promises and/or platform",
                'photo_url': candidate_data['picture']['large']
            }
        else:
            return "Error fetching candidate data"
        
    def insert_candidates(self, candidate_data):
        self.cur.execute(
            """
                INSERT INTO candidates(candidate_id, candidate_name, party_affiliation, biography, campaign_platform, photo_url)
                VALUES(%s, %s, %s, %s, %s, %s)
            """,
            (
                candidate_data["candidate_id"], candidate_data["candidate_name"], candidate_data["party_affiliation"], 
                candidate_data["biography"], candidate_data["campaign_platform"], candidate_data["photo_url"]
            )
        )
        self.conn.commit()

    def populate_voter_data():
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            voter_data = response.json()['results'][0]
            return {
                "voter_id": voter_data['login']['uuid'],
                "voter_name": f"{voter_data['name']['first']} {voter_data['name']['last']}",
                "date_of_birth": voter_data['dob']['date'],
                "gender": voter_data['gender'],
                "nationality": voter_data['nat'],
                "registration_number": voter_data['login']['username'],
                "address": {
                    "street": f"{voter_data['location']['street']['name']} {voter_data['location']['street']['number']}",
                    "city": voter_data['location']['city'],
                    "state": voter_data['location']['state'],
                    "country": voter_data['location']['country'],
                    "postcode": voter_data['location']['postcode']
                },
                "email": voter_data['email'],
                "phone_number": voter_data['phone'],
                "picture": voter_data['picture']['large'],
                "registered_age": voter_data['registered']['age']
            }

    def insert_voters(self, voter_data):
        self.cur.execute(
            """
                INSERT INTO voters(voter_id, voter_name, date_of_birth, gender, nationality, registration_number, 
                    address_street, address_city, address_state, address_country, address_postcode, phone_number, picture, registered_age)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                voter_data["voter_id"], voter_data["voter_name"], voter_data["date_of_birth"], voter_data["gender"], voter_data["nationality"], 
                voter_data["registration_number"], voter_data["address"]["street"], voter_data["address"]["city"], voter_data["address"]["state"],
                voter_data["address"]["country"], voter_data["address"]["postcode"], voter_data["phone_number"], voter_data["picture"], voter_data["registered_age"]
            )
        )
        self.conn.commit()

    def insert_votes(self, vote):
        self.cur.execute(
            """
                INSERT INTO voters(voter_id, candidate_id, voting_time)
                VALUES(%s, %s, %s)
            """,
            (
                vote["voter_id"], vote["candidate_id"], vote["voting_time"]
            )
        )
        self.conn.commit()