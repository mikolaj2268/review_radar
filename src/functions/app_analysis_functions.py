# src/functions/app_analysis_functions.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from src.database_connection.db_utils import (
    get_reviews_date_ranges,
    get_reviews_for_app
)
from src.functions.scraper import scrape_and_store_reviews

def plot_content_length_distribution(df):
    """
    Plot the distribution of content length.
    Parameters:
    df (pd.DataFrame): The input DataFrame containing the reviews.
    Returns:
    plotly.graph_objs._figure.Figure: The Plotly figure object.
    """
    fig = px.histogram(df, x='content_length', nbins=30, title='Distribution of Content Length')
    fig.update_layout(xaxis_title='Content Length', yaxis_title='Count')
    return fig

def plot_score_distribution(df):
    """
    Plot the distribution of scores.
    Parameters:
    df (pd.DataFrame): The input DataFrame containing the reviews.
    Returns:
    plotly.graph_objs._figure.Figure: The Plotly figure object.
    """
    fig = px.histogram(df, x='score', nbins=5, title='Distribution of Scores')
    fig.update_layout(xaxis_title='Score', yaxis_title='Count')
    return fig

def preprocess_data(df):
    """
    Preprocess the given DataFrame.
    Parameters:
    df (pd.DataFrame): The input DataFrame to preprocess.
    Returns:
    pd.DataFrame: The preprocessed DataFrame.
    """
    # Drop duplicates
    df = df.drop_duplicates()

    # Handle missing values
    df['content'] = df['content'].fillna('')
    df['review_created_version'] = df['review_created_version'].fillna('Unknown')
    df['app_version'] = df['app_version'].fillna('Unknown')
    df['reply_content'] = df['reply_content'].fillna('')
    df['replied_at'] = df['replied_at'].fillna(pd.NaT)

    # Convert 'at' to datetime and create 'date' column
    df['at'] = pd.to_datetime(df['at'], errors='coerce')
    df = df.dropna(subset=['at'])  # Remove rows with invalid dates
    df['date'] = df['at'].dt.date

    # Convert other date columns to datetime
    date_columns = ['replied_at']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Remove rows with invalid scores
    df = df[(df['score'] >= 1) & (df['score'] <= 5)]

    # Normalize text in 'content' column
    df['content'] = df['content'].str.lower().str.replace(r'[^\w\s]', '', regex=True)

    # Add new feature: length of the review content
    df['content_length'] = df['content'].apply(len)

    # Handle missing app_version intelligently
    df = df.sort_values(by='at')
    df['app_version'] = df['app_version'].replace('Unknown', pd.NA)
    df['app_version'] = df['app_version'].ffill()

    # Drop unnecessary columns
    columns_to_drop = ['user_image', 'reply_content', 'replied_at']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    # Handle outliers in thumbs_up_count
    if 'thumbs_up_count' in df.columns:
        df['thumbs_up_count'] = df['thumbs_up_count'].clip(lower=0)

    return df

def search_and_select_app(search_query):
    # Search for apps via select_app function
    from src.functions.scraper import select_app
    search_results = select_app(search_query)
    return search_results

def check_and_fetch_reviews(conn, selected_app, selected_app_id, start_date, end_date):
    # Get existing review dates for the app
    existing_dates = get_reviews_date_ranges(conn, selected_app)

    # Identify missing and available date ranges
    missing_ranges = get_missing_and_available_ranges(existing_dates, start_date, end_date)

    if not missing_ranges['missing']:
        st.success(f"Reviews for {selected_app} from {start_date} to {end_date} are up-to-date.")
    else:
        # Display missing date ranges
        st.warning("Data is incomplete. Fetching missing reviews...")
        for missing_range in missing_ranges['missing']:
            st.info(f"- Missing: {missing_range[0]} to {missing_range[1]}")

        # Fetch missing reviews
        fetch_missing_reviews(conn, selected_app, selected_app_id, missing_ranges['missing'])

        if not st.session_state.get('stop_download'):
            st.success("All missing reviews have been fetched.")

def get_missing_and_available_ranges(existing_dates, start_date, end_date):
    total_date_set = set(start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1))
    missing_date_set = total_date_set - existing_dates
    available_date_set = existing_dates & total_date_set

    # Convert date sets into sorted lists
    missing_dates = sorted(missing_date_set)
    available_dates = sorted(available_date_set)

    # Convert dates into continuous ranges
    missing_ranges = dates_to_ranges(missing_dates)
    available_ranges = dates_to_ranges(available_dates)

    return {
        'missing': missing_ranges,
        'available': available_ranges
    }

def dates_to_ranges(dates_list):
    """Converts a sorted list of dates into a list of continuous date ranges."""
    if not dates_list:
        return []

    ranges = []
    start_date = dates_list[0]
    end_date = dates_list[0]

    for date in dates_list[1:]:
        if date == end_date + timedelta(days=1):
            end_date = date
        else:
            ranges.append((start_date, end_date))
            start_date = date
            end_date = date

    ranges.append((start_date, end_date))
    return ranges

def fetch_missing_reviews(conn, selected_app, selected_app_id, missing_ranges):
    for index, date_range in enumerate(missing_ranges):
        start_date = date_range[0]
        end_date = date_range[1]
        if st.session_state.get('stop_download'):
            st.warning("Download process stopped by user.")
            break

        st.info(f"Fetching reviews from {start_date} to {end_date}...")

        # Initialize progress bar and text placeholders for this range
        progress_bar = st.progress(0)
        progress_text = st.empty()

        # Fetch reviews for this date range
        scrape_and_store_reviews(
            app_name=selected_app,
            app_id=selected_app_id,
            conn=conn,
            progress_bar=progress_bar,
            progress_text=progress_text,
            start_date=start_date,
            end_date=end_date,
            country="us",
            language="en",
        )

        # Clear progress bar and text for this range
        progress_bar.empty()
        progress_text.empty()

    if not st.session_state.get('stop_download'):
        st.success("Finished fetching missing reviews.")

def display_reviews(conn, selected_app, start_date, end_date):
    # Fetch reviews from the database
    reviews_df = get_reviews_for_app(conn, selected_app, start_date, end_date)
    return reviews_df

def get_db_connection():
    from src.database_connection.db_utils import get_db_connection as db_get_db_connection
    return db_get_db_connection()

def create_tables(conn):
    from src.database_connection.db_utils import create_reviews_table
    create_reviews_table(conn)