import psycopg2

def postgre_create_tables(conn, cur):
    cur.execute(
        """
            
        """
    )

if __name__ == "__main__":
    try:
        conn = psycopg2.connect("host=localhost dbname=votingDB user=kekuser password=kekpwd")
        cur = conn.cursor()


    except Exception as e:
        print(f"Unable to create tables/connect to the postgre DB: {e}")