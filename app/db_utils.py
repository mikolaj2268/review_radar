# db_utils.py

import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host="localhost",
        database="google_play_reviews",
        user="postgres",
        password="password"
    )
    return conn


def get_app_names(conn):
    """Fetches a list of distinct application names from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT app_name FROM app_reviews;")
    apps_in_db = cursor.fetchall()
    cursor.close()
    app_names = [app[0] for app in apps_in_db]
    return app_names

def get_reviews_for_app(conn, app_name):
    """Retrieves all reviews for a specified application."""
    query = """
    SELECT user_name, content, score, at 
    FROM app_reviews 
    WHERE app_name = %s 
    ORDER BY at DESC;
    """
    reviews_df = pd.read_sql_query(query, conn, params=(app_name,))
    return reviews_df

def create_reviews_table(conn):
    """Creates the app_reviews table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_reviews (
            review_id VARCHAR(255) PRIMARY KEY,
            user_name VARCHAR(255),
            user_image TEXT,
            content TEXT,
            score INT,
            thumbs_up_count INT,
            review_created_version VARCHAR(50),
            at TIMESTAMP,
            reply_content TEXT,
            replied_at TIMESTAMP,
            app_version VARCHAR(50),
            app_name VARCHAR(255),
            country VARCHAR(10),
            language VARCHAR(10)
        );
    ''')
    conn.commit()
    cursor.close()

def get_app_id(app_name):
    """Gets the app ID based on the app name."""
    try:
        search_results = search(app_name, n_hits=1, lang='en', country='us')
        if search_results:
            app_id = search_results[0]['appId']
            return app_id
        else:
            return None
    except Exception as e:
        print(f"Error searching for app '{app_name}': {e}")
        return None
