# src/database_connection/db_utils.py

import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

# Wczytaj zmienne środowiskowe z pliku .env
load_dotenv()

def get_db_connection():
    """Nawiązuje połączenie z bazą danych SQLite."""
    conn = sqlite3.connect('google_play_reviews.db')
    return conn

def create_reviews_table(conn):
    """Tworzy tabelę app_reviews, jeśli nie istnieje."""
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
    """Pobiera dostępne zakresy dat recenzji dla aplikacji."""
    cursor = conn.cursor()
    query = """
    SELECT MIN(at), MAX(at) FROM app_reviews 
    WHERE app_name = ? AND at IS NOT NULL
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
    """Pobiera recenzje dla określonej aplikacji w zadanym zakresie dat."""
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
    """Pobiera pełne dane dla określonej aplikacji w zadanym zakresie dat."""
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