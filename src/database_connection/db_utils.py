# src/database_connection/db_utils.py

from google_play_scraper import search
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

def get_reviews_date_ranges(conn, app_name):
    """Gets all available review date ranges for an app."""
    cursor = conn.cursor()
    query = """
    SELECT MIN(at), MAX(at) FROM app_reviews 
    WHERE app_name = %s AND at IS NOT NULL
    GROUP BY DATE(at)
    """
    cursor.execute(query, (app_name,))
    results = cursor.fetchall()
    cursor.close()
    if results:
        date_ranges = [(row[0], row[1]) for row in results]
        date_ranges.sort(key=lambda x: x[0])
        return date_ranges
    else:
        return []

def get_reviews_for_app(conn, app_name, start_date=None, end_date=None):
    """Retrieves reviews for a specified application within a date range."""
    query = """
    SELECT user_name, content, score, at 
    FROM app_reviews 
    WHERE app_name = %s
    """
    params = [app_name]
    if start_date:
        query += " AND at >= %s"
        params.append(start_date)
    if end_date:
        query += " AND at <= %s"
        params.append(end_date)
    query += " ORDER BY at DESC;"
    reviews_df = pd.read_sql_query(query, conn, params=params)
    return reviews_df

# get whole app data
def get_app_data(conn, app_name, start_date=None, end_date=None):
    """Retrieves data for a specified application within a date range."""
    query = """
    SELECT *
    FROM app_reviews 
    WHERE app_name = %s
    """
    params = [app_name]
    if start_date:
        query += " AND at >= %s"
        params.append(start_date)
    if end_date:
        query += " AND at <= %s"
        params.append(end_date)
    query += " ORDER BY at DESC;"
    reviews_df = pd.read_sql_query(query, conn, params=params)
    return reviews_df