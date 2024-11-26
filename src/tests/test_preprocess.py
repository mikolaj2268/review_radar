# We will test the preprocess_data function from the app_analysis_functions.py file
import sys
import os
from transformers import AutoTokenizer

# Dodaj ścieżkę do katalogu `src`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import numpy as np
import streamlit as st

from src.functions.app_analysis_functions import preprocess_data
from src.database_connection.db_utils import get_db_connection, get_app_data, create_reviews_table

def main():
    # Connect to the database
    conn = get_db_connection()
    
    # Create the app_reviews table if it doesn't exist
    create_reviews_table(conn)
    
    # Get the data for a specific app (replace 'YourAppName' with the actual app name)
    app_name = 'Netflix'
    app_data = get_app_data(conn, app_name)
    
    # Display the data before preprocessing
    st.write("Data before preprocessing:")
    st.dataframe(app_data)
    
    # Preprocess the data
    preprocessed_data = preprocess_data(app_data, model='VADER', min_records=100, apply_lemmatization=True, correct_spelling=False)
    
    # Display the data after preprocessing
    st.write("Data after preprocessing:")
    st.dataframe(preprocessed_data)
    
    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()