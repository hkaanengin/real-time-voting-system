import psycopg2
import requests
import random

BASE_URL = "https://randomuser.me/api/?nat=tr"
PARTIES = ['AKP', 'CHP', 'MHP', 'Iyi Parti']
NUMBER_OF_VOTERS = 1000

random.seeds(20)

##Move generation methods into a different folder&class

def postgre_create_tables(conn, cur):
    cur.execute(
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

    cur.execute(
        """
            CREATE TABLE IF NOT EXISTS voters (
                voter_id VARCHAR(255) PRIMARY KEY,
                voter_name VARCHAR(255),
                date_of_birth DATE VARCHAR(255),
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
                registered_age INTEGER,
            )
        """
    )

    cur.execute(
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

    conn.commit()

def generate_candidate_data(candidate_number, total_parties):
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
    
def insert_candidates(conn, cur, candidate_data):
    cur.execute(
        """
            INSERT INTO candidates(candidate_id, candidate_name, party_affiliation, biography, campaign_platform, photo_url)
            VALUES(%s, %s, %s, %s, %s, %s)
        """,
        (
            candidate_data["candidate_id"], candidate_data["candidate_name"], candidate_data["party_affiliation"], 
            candidate_data["biography"], candidate_data["campaign_platform"], candidate_data["photo_url"]
        )
    )
    conn.commit()

def generate_voter_data():
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

def insert_voters(conn, cur, voter_data):
    cur.execute("""
            INSERT INTO candidates(voter_id, voter_name, date_of_birth, gender, nationality, registration_number, 
                address_street, address_city, address_state, address_country, address_postcode, phone_number, picture, registered_age)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            voter_data["voter_id"], voter_data["voter_name"], voter_data["date_of_birth"], voter_data["gender"], voter_data["nationality"], 
            voter_data["registration_number"], voter_data["address"]["street"], voter_data["address"]["city"], voter_data["address"]["state"],
            voter_data["address"]["country"], voter_data["address"]["postcode"], voter_data["email"], voter_data["phone_number"], 
            voter_data["picture"], voter_data["registered_age"]
        )
    )
    conn.commit()

if __name__ == "__main__":
    try:
        conn = psycopg2.connect("host=localhost dbname=votingDB user=kekuser password=kekpwd")
        cur = conn.cursor()
        postgre_create_tables(conn, cur)

        cur.execute("""
            SELECT * FROM candidates
        """)
        candidates = cur.fetchall()

        if len(candidates) == 0:
            for i in range(len(PARTIES)):  #refactor this part
                candidate = generate_candidate_data(i, len(PARTIES))
                insert_candidates(conn, cur, candidate)

        for i in range(NUMBER_OF_VOTERS):
            voter_data = generate_voter_data()
            insert_voters(conn, cur, voter_data)
        else:
            print("There are candidates present in the 'candidates' table")
    except Exception as e:
        print(f"Unable to create tables/connect to the postgre DB: {e}")