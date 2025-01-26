import sys
import os
from transformers import AutoTokenizer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import numpy as np
import streamlit as st

from src.functions.app_analysis_functions import preprocess_data
from src.database_connection.db_utils import get_db_connection, get_app_data, create_reviews_table

def main():
    conn = get_db_connection()
    
    create_reviews_table(conn)
    
    app_name = 'Netflix'
    app_data = get_app_data(conn, app_name)
    
    st.write("Data before preprocessing:")
    st.dataframe(app_data)

    preprocessed_data = preprocess_data(app_data, model='VADER', min_records=100, apply_lemmatization=True, correct_spelling=False)
    
    st.write("Data after preprocessing:")
    st.dataframe(preprocessed_data)
    
    conn.close()

if __name__ == "__main__":
    main()