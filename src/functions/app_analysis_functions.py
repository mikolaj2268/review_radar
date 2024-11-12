# src/functions/app_analysis_functions.py

import streamlit as st
from datetime import datetime, timedelta
from src.database_connection.db_utils import (
    get_reviews_date_ranges,
    get_reviews_for_app
)
from src.functions.scraper import scrape_and_store_reviews  

def search_and_select_app(search_query):
    # Search for apps via select_app function
    from src.functions.scraper import select_app
    search_results = select_app(search_query)
    return search_results

def check_and_fetch_reviews(conn, selected_app, selected_app_id, start_date, end_date):
    # Get existing review date ranges for the app
    existing_ranges = get_reviews_date_ranges(conn, selected_app)

    # Identify missing and available date ranges
    missing_ranges = get_missing_and_available_ranges(existing_ranges, start_date, end_date)

    if not missing_ranges['missing']:
        st.success(f"Reviews for this application from {start_date.date()} to {end_date.date()} are up-to-date.")
    else:
        # Display missing date ranges
        st.warning("Data is incomplete. Fetching missing reviews...")
        for missing_range in missing_ranges['missing']:
            st.info(f"- Missing: {missing_range['start'].date()} to {missing_range['end'].date()}")

        # Fetch missing reviews
        fetch_missing_reviews(conn, selected_app, selected_app_id, missing_ranges['missing'])

        if not st.session_state.stop_download:
            st.success("All missing reviews have been fetched.")

def get_missing_and_available_ranges(existing_ranges, start_date, end_date):
    """Identifies missing and available date ranges within the selected date range."""
    total_days = (end_date.date() - start_date.date()).days + 1
    all_dates = [start_date.date() + timedelta(days=i) for i in range(total_days)]

    existing_dates = set()
    for range_start, range_end in existing_ranges:
        days_in_range = (range_end.date() - range_start.date()).days + 1
        existing_dates.update(range_start.date() + timedelta(days=i) for i in range(days_in_range))

    missing_dates = set(all_dates) - existing_dates

    # Group continuous dates into ranges
    missing_ranges = dates_to_ranges(sorted(missing_dates))
    available_ranges = dates_to_ranges(sorted(existing_dates.intersection(all_dates)))

    return {'missing': missing_ranges, 'available': available_ranges}

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
            ranges.append({
                'start': datetime.combine(start_date, datetime.min.time()), 
                'end': datetime.combine(end_date, datetime.max.time())
            })
            start_date = date
            end_date = date
    ranges.append({
        'start': datetime.combine(start_date, datetime.min.time()), 
        'end': datetime.combine(end_date, datetime.max.time())
    })
    return ranges

def fetch_missing_reviews(conn, selected_app, selected_app_id, missing_date_ranges):
    for date_range in missing_date_ranges:
        if st.session_state.get('stop_download'):
            st.warning("Download process stopped by user.")
            break

        start_date = date_range['start']
        end_date = date_range['end']

        st.info(f"Fetching reviews from {start_date.date()} to {end_date.date()}...")

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

        if st.session_state.get('stop_download'):
            st.warning("Download process stopped by user.")
            break

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