import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

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
    """Fetches distinct review dates for a specific app."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT date(at) as review_date FROM app_reviews WHERE app_name = ?
    ''', (app_name,))
    dates = cursor.fetchall()
    cursor.close()
    
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

def insert_reviews(conn, reviews_df):
    """Insert reviews into the database, ignoring duplicates based on review_id."""
    cursor = conn.cursor()
    insert_query = '''
        INSERT OR IGNORE INTO app_reviews (
            review_id, user_name, user_image, content, score, thumbs_up_count,
            review_created_version, at, reply_content, replied_at, app_version,
            app_name, country, language
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    '''
    for _, row in reviews_df.iterrows():
        cursor.execute(insert_query, (
            row['review_id'],
            row['user_name'],
            row['user_image'],
            row['content'],
            row['score'],
            row['thumbs_up_count'],
            row['review_created_version'],
            row['at'].isoformat(),
            row['reply_content'],
            row['replied_at'].isoformat() if row['replied_at'] else None,
            row['app_version'],
            row['app_name'],
            row['country'],
            row['language']
        ))
    conn.commit()
    cursor.close()