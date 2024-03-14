import streamlit as st
import time
from src.postgre_actions import PostgreActions

def fetch_voting_stats():
    cur = PostgreActions().get_cur()
    
    #Fetch total number of voters
    cur.execute(
        """
            SELECT count(*) voters_count from voters
        """
    )
    voters_count = cur.fetchone()[0]

    #Fetch total number of candidates
    cur.execute(
        """
            SELECT count(*) candidates_count from candidates
        """
    )
    candidates_count = cur.fetchone()[0]


def update_data():
    last_refresh = st.empty()
    last_refresh.text(f"Last refresh at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    fetch_voting_stats()