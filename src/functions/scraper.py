# src/functions/scraper.py

import sqlite3
import pandas as pd
from google_play_scraper import Sort, reviews, search
from datetime import datetime, timedelta
import streamlit as st

def select_app(app_name):
    """Searches for apps matching the input name and returns a list of options."""
    try:
        search_results = search(app_name, n_hits=5, lang='en', country='us')
        return search_results
    except Exception as e:
        st.error(f"Error searching for app '{app_name}': {e}")
        return []

def scrape_and_store_reviews(app_name, app_id, conn, progress_bar=None, progress_text=None, start_date=None, end_date=None, country='us', language='en'):
    """Scrapes reviews and stores them in the SQLite database with a progress bar based on date range."""
    cursor = conn.cursor()

    # Ensure start_date and end_date are datetime objects
    if not isinstance(start_date, datetime):
        start_date = datetime.combine(start_date, datetime.min.time())
    if not isinstance(end_date, datetime):
        end_date = datetime.combine(end_date, datetime.max.time())

    if not start_date:
        start_date = datetime.now() - timedelta(days=7)
    if not end_date:
        end_date = datetime.now()

    total_reviews_fetched = 0
    continuation_token = None

    # Calculate total seconds in the date range
    total_seconds = (end_date - start_date).total_seconds() or 1  # Prevent division by zero

    oldest_review_date_fetched = end_date  # Initialize with end_date

    while True:
        if st.session_state.get('stop_download'):
            st.warning("Download stopped by user.")
            break

        try:
            new_reviews, continuation_token = reviews(
                app_id,
                lang=language,
                country=country,
                sort=Sort.NEWEST,
                count=200,
                continuation_token=continuation_token
            )
        except Exception as e:
            st.error(f"Error fetching reviews for {app_name}: {e}")
            break

        if not new_reviews:
            break

        # Filter reviews within the date range
        new_reviews_in_range = [review for review in new_reviews if start_date <= review['at'] <= end_date]

        # Check if no reviews are in the desired date range
        if not new_reviews_in_range:
            # If the oldest review in the batch is older than start_date, we can stop
            if new_reviews[-1]['at'] < start_date:
                break
            else:
                # Continue to next batch
                continue

        # Add all reviews in range to the total count
        total_reviews_fetched += len(new_reviews_in_range)

        # Update oldest_review_date_fetched
        oldest_review_date_in_batch = new_reviews_in_range[-1]['at']
        if oldest_review_date_in_batch < oldest_review_date_fetched:
            oldest_review_date_fetched = oldest_review_date_in_batch

        # Calculate progress based on the date range
        elapsed_seconds = (end_date - oldest_review_date_fetched).total_seconds()
        progress = min(max(elapsed_seconds / total_seconds, 0), 1)  # Ensure progress is between 0 and 1

        # Update progress bar and text
        if progress_bar is not None and progress_text is not None:
            progress_bar.progress(progress)
            progress_text.write(f"**{app_name}: Fetched {total_reviews_fetched} reviews so far...** Progress: {progress*100:.2f}%")

        # Prepare DataFrame
        reviews_df = pd.DataFrame(new_reviews_in_range)
        reviews_df['app_name'] = app_name
        reviews_df['country'] = country
        reviews_df['language'] = language

        # Replace NaT and NaN values with None
        reviews_df = reviews_df.replace({pd.NaT: None})
        reviews_df = reviews_df.where(pd.notnull(reviews_df), None)

        # Convert datetime fields to strings
        datetime_fields = ['at', 'repliedAt']
        for field in datetime_fields:
            if field in reviews_df.columns:
                reviews_df[field] = reviews_df[field].apply(lambda x: x.isoformat() if x is not None else None)

        # Prepare the SQL statement with '?' placeholders
        insert_query = '''
            INSERT INTO app_reviews (
                review_id, user_name, user_image, content, score, thumbs_up_count,
                review_created_version, at, reply_content, replied_at, app_version,
                app_name, country, language
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(review_id) DO NOTHING;
        '''

        # Insert reviews into the database
        for _, row in reviews_df.iterrows():
            cursor.execute(insert_query, (
                row['reviewId'],
                row['userName'],
                row['userImage'],
                row['content'],
                row['score'],
                row['thumbsUpCount'],
                row.get('reviewCreatedVersion', None),
                row['at'],  # Converted to string
                row.get('replyContent', None),
                row.get('repliedAt', None),  # Converted to string
                row.get('appVersion', None),
                app_name,
                country,
                language
            ))
        conn.commit()

        # Check if the oldest review fetched is older than the start_date
        if oldest_review_date_fetched <= start_date:
            break

        if continuation_token is None:
            break

    cursor.close()

    # Final progress message
    if progress_bar is not None and progress_text is not None:
        progress_bar.progress(1.0)
        if st.session_state.get('stop_download'):
            progress_text.write(f"**Download stopped. Total reviews fetched: {total_reviews_fetched}.**")
        else:
            progress_text.write(f"**Finished downloading reviews for {app_name}. Total reviews fetched: {total_reviews_fetched}.**")