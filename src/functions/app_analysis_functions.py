import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from transformers import AutoTokenizer
from src.database_connection.db_utils import (
    get_reviews_date_ranges,
    get_reviews_for_app
)
from src.functions.scraper import scrape_and_store_reviews
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
    

def plot_daily_average_rating(data):
    """
    Generate a line plot of the daily average rating over time.

    Parameters:
    - data (pd.DataFrame): DataFrame containing at least 'at' (datetime) and 'score' columns.

    Returns:
    - plotly.graph_objects.Figure: The generated line plot.
    """

    data['at'] = pd.to_datetime(data['at'])

    daily_avg_rating = data.groupby(data['at'].dt.date)['score'].mean().reset_index()
    daily_avg_rating.columns = ['Date', 'Average Score']

    fig = px.line(
        daily_avg_rating,
        x="Date",
        y="Average Score",
        title="Daily Average Rating Over Time",
        labels={"Date": "Date", "Average Score": "Average Rating"},
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Average Rating",
        yaxis=dict(range=[1, 5])
    )

    return fig

def preprocess_text_simple(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return ' '.join(filtered_words)

def generate_ngrams(text, n):
    words = text.split()
    ngrams = [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]
    return ngrams


def plot_content_length_distribution(df):
    """
    Plot the distribution of content length.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame containing the reviews.
    """
    fig = px.histogram(df, x='content_length', nbins=30, title='Distribution of Content Length')
    fig.update_layout(xaxis_title='Content Length', yaxis_title='Count')
    return fig

def plot_score_distribution(df):
    """
    Plot the distribution of scores as percentages.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame containing the reviews and a 'score' column.
    """

    score_counts = df['score'].value_counts(normalize=True).sort_index()
    score_distribution_df = score_counts.reset_index()
    score_distribution_df.columns = ['Score', 'Percentage']
    
    fig = px.bar(
        score_distribution_df,
        x='Score',
        y='Percentage',
        title='Distribution of Scores',
        category_orders={'Score': [1, 2, 3, 4, 5]},
        text='Percentage',
        color_discrete_sequence=['#2196F3']
    )
    
    fig.update_layout(
        xaxis_title='Score',
        yaxis_title='Percentage',
        yaxis=dict(tickformat=".0%")
    )
    
    fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')
    
    return fig



def preprocess_data(df, model=None, min_records=100, apply_lemmatization=True):
    """
    Preprocess the given DataFrame for sentiment analysis and visualization.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame to preprocess.
    model (str, optional): The sentiment analysis model ('VADER' or 'Transformers').
    min_records (int, optional): Minimum records required for reliable analysis.
    apply_lemmatization (bool, optional): Whether to apply lemmatization to the text.
    correct_spelling (bool, optional): Whether to correct spelling errors in the text.

    Returns:
    pd.DataFrame: The preprocessed DataFrame.
    """
    
    if df.empty:
        raise ValueError("The input DataFrame is empty. Please provide a valid DataFrame.")

    columns_to_drop = ['c_name', 'user_image', 'reply_content', 'replied_at', 'review_created_version', 'review_id']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')

    df = df.drop_duplicates()
    df = df[(df['score'] >= 1) & (df['score'] <= 5)]
    df = df[df['content'].str.len() <= 500]
    for col in ['content', 'app_version']:
        df[col] = df[col].fillna('')

    df['at'] = pd.to_datetime(df['at'], errors='coerce')
    df = df.dropna(subset=['at']) 
    df['date'] = df['at'].dt.date

    df['content'] = df['content'].str.lower()

    if model == 'VADER':
        df['clean_content'] = df['content'].str.replace(r'[^\w\s]', '', regex=True)
        
    if model == 'Transformers':
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")  
        df['tokens'] = df['content'].apply(lambda x: tokenizer.tokenize(x))


    if len(df) < min_records:
        print(f"Warning: The dataset contains only {len(df)} records. Consider collecting more data.")
    
    df['content_length'] = df['content'].str.len()
    if 'thumbs_up_count' in df.columns:
        df['thumbs_up_count'] = df['thumbs_up_count'].clip(lower=0)
    
    
    return df

def search_and_select_app(search_query):
    """
    Search for applications based on the search query.
    
    Parameters:
    search_query (str): The search term entered by the user.
    
    Returns:
    list: A list of search results.
    """
    from src.functions.scraper import select_app
    search_results = select_app(search_query)
    return search_results

def check_and_fetch_reviews(conn, selected_app, selected_app_id, start_date, end_date, status_placeholder, missing_placeholder):
    """
    Check for missing reviews and fetch them if necessary.
    
    Parameters:
    conn: Database connection object.
    selected_app (str): The name of the selected application.
    selected_app_id (str): The ID of the selected application.
    start_date (datetime): The start date for fetching reviews.
    end_date (datetime): The end date for fetching reviews.
    status_placeholder: Streamlit placeholder for status messages.
    missing_placeholder: Streamlit placeholder for missing date ranges.
    """
    
    existing_dates = get_reviews_date_ranges(conn, selected_app)

   
    missing_ranges = get_missing_and_available_ranges(existing_dates, start_date, end_date)

    if not missing_ranges['missing']:
        status_placeholder.success(f"Reviews for **{selected_app}** from {start_date} to {end_date} are up-to-date.")
    else:
        # Display missing date ranges
        for missing_range in missing_ranges['missing']:
            missing_placeholder.info(f"- Missing: {missing_range[0]} to {missing_range[1]}")

        # Fetch missing reviews
        fetch_missing_reviews(conn, selected_app, selected_app_id, missing_ranges['missing'], status_placeholder, missing_placeholder)

        # Clear placeholders after fetching
        status_placeholder.empty()
        missing_placeholder.empty()

        if not st.session_state.get('stop_download'):
            status_placeholder.success("All missing reviews have been fetched.")

def fetch_missing_reviews(conn, selected_app, selected_app_id, missing_ranges, status_placeholder, missing_placeholder):
    """
    Fetch and store missing reviews for the specified date ranges.
    
    Parameters:
    conn: Database connection object.
    selected_app (str): The name of the selected application.
    selected_app_id (str): The ID of the selected application.
    missing_ranges (list of tuples): List of missing date ranges.
    status_placeholder: Streamlit placeholder for status messages.
    missing_placeholder: Streamlit placeholder for missing date ranges.
    """
    for index, date_range in enumerate(missing_ranges):
        start_date = date_range[0]
        end_date = date_range[1]
        if st.session_state.get('stop_download'):
            status_placeholder.warning("Download process stopped by user.")
            break

        fetch_placeholder = st.empty()
        fetch_placeholder.info(f"Fetching reviews from {start_date} to {end_date}...")

        progress_bar = st.progress(0)
        progress_text = st.empty()

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

        progress_bar.empty()
        progress_text.empty()
        fetch_placeholder.empty()

    if not st.session_state.get('stop_download'):
        status_placeholder.success("Finished fetching missing reviews.")

def get_missing_and_available_ranges(existing_dates, start_date, end_date):
    """
    Calculate missing and available date ranges based on existing data.
    
    Parameters:
    existing_dates (set): Set of existing dates with reviews.
    start_date (datetime): The start date for fetching reviews.
    end_date (datetime): The end date for fetching reviews.
    
    Returns:
    dict: Dictionary containing 'missing' and 'available' date ranges.
    """
    total_date_set = set(start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1))
    missing_date_set = total_date_set - existing_dates
    available_date_set = existing_dates & total_date_set

    missing_dates = sorted(missing_date_set)
    available_dates = sorted(available_date_set)

    missing_ranges = dates_to_ranges(missing_dates)
    available_ranges = dates_to_ranges(available_dates)

    return {
        'missing': missing_ranges,
        'available': available_ranges
    }

def dates_to_ranges(dates_list):
    """
    Convert a sorted list of dates into continuous date ranges.
    
    Parameters:
    dates_list (list): Sorted list of datetime objects.
    
    Returns:
    list of tuples: List containing tuples of (start_date, end_date).
    """
    if not dates_list:
        return []

    ranges = []
    start_date = dates_list[0]
    end_date = dates_list[0]

    for current_date in dates_list[1:]:
        if current_date == end_date + timedelta(days=1):
            end_date = current_date
        else:
            ranges.append((start_date, end_date))
            start_date = current_date
            end_date = current_date

    ranges.append((start_date, end_date))
    return ranges

def display_reviews(conn, selected_app, start_date, end_date):
    """
    Fetch and return reviews for the selected application within the specified date range.
    
    Parameters:
    conn: Database connection object.
    selected_app (str): The name of the selected application.
    start_date (datetime): The start date for fetching reviews.
    end_date (datetime): The end date for fetching reviews.
    
    Returns:
    pd.DataFrame: DataFrame containing the fetched reviews.
    """

    reviews_df = get_reviews_for_app(conn, selected_app, start_date, end_date)
    return reviews_df

def get_db_connection():
    """
    Establish and return a database connection.
    
    Returns:
    Connection object: The database connection.
    """
    from src.database_connection.db_utils import get_db_connection as db_get_db_connection
    return db_get_db_connection()

def create_tables(conn):
    """
    Create necessary tables in the database.
    
    Parameters:
    conn: Database connection object.
    """
    from src.database_connection.db_utils import create_reviews_table
    create_reviews_table(conn)