# src/database_connection/db_utils.py

import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('google_play_reviews.db')
    return conn

def create_reviews_table(conn):
    """Creates the app_reviews table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_reviews (
            review_id TEXT PRIMARY KEY,
            user_name TEXT,
            user_image TEXT,
            content TEXT,
            score INTEGER,
            thumbs_up_count INTEGER,
            review_created_version TEXT,
            at TIMESTAMP,
            reply_content TEXT,
            replied_at TIMESTAMP,
            app_version TEXT,
            app_name TEXT,
            country TEXT,
            language TEXT
        );
    ''')
    conn.commit()
    cursor.close()

def get_reviews_date_ranges(conn, app_name):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT date(at) as review_date FROM app_reviews WHERE app_name = ?
    ''', (app_name,))
    dates = cursor.fetchall()
    cursor.close()
    # Convert list of tuples to a set of dates
    existing_dates = set(date[0] for date in dates if date[0])
    return existing_dates

def get_reviews_for_app(conn, app_name, start_date=None, end_date=None):
    """Fetches reviews for a specific application within the given date range."""
    query = """
    SELECT user_name, content, score, at 
    FROM app_reviews 
    WHERE app_name = ?
    """
    params = [app_name]
    if start_date:
        query += " AND at >= ?"
        params.append(start_date)
    if end_date:
        query += " AND at <= ?"
        params.append(end_date)
    query += " ORDER BY at DESC;"
    reviews_df = pd.read_sql_query(query, conn, params=params)
    return reviews_df

def get_app_data(conn, app_name, start_date=None, end_date=None):
    """Fetches complete data for a specific application within the given date range."""
    query = """
    SELECT *
    FROM app_reviews 
    WHERE app_name = ?
    """
    params = [app_name]
    if start_date:
        query += " AND at >= ?"
        params.append(start_date)
    if end_date:
        query += " AND at <= ?"
        params.append(end_date)
    query += " ORDER BY at DESC;"
    reviews_df = pd.read_sql_query(query, conn, params=params)
    return reviews_df