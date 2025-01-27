import sqlite3
import pandas as pd
from google_play_scraper import Sort, reviews, search
from datetime import datetime, timedelta
import streamlit as st

def select_app(app_name):
    """Searches for apps matching the input name and returns a list of options."""
    try:
        search_results = search(app_name, n_hits=5, lang='en', country='us')
        
        if not isinstance(search_results, list):
            st.error(f"Unexpected response format when searching for '{app_name}'.")
            return []
        
        search_results = [app for app in search_results if app is not None]
        
        if not search_results:
            st.warning(f"No apps found matching '{app_name}'. Please try a different name.")
        
        return search_results
    
    except Exception as e:
        st.error(f"Error searching for app '{app_name}': {e}")
        return []
    
    except Exception as e:
        st.error(f"Error searching for app '{app_name}': {e}")
        return []

def scrape_and_store_reviews(app_name, app_id, conn, progress_bar=None, progress_text=None, start_date=None, end_date=None, country='us', language='en'):
    """Scrapes reviews and stores them in the SQLite database with a progress bar based on date range."""
    cursor = conn.cursor()

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

    total_seconds = (end_date - start_date).total_seconds() or 1

    oldest_review_date_fetched = end_date

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

        new_reviews_in_range = [review for review in new_reviews if start_date <= review['at'] <= end_date]

        if not new_reviews_in_range:
            if new_reviews and new_reviews[-1]['at'] < start_date:
                break
            elif not new_reviews:
                break
            else:
                continue

        total_reviews_fetched += len(new_reviews_in_range)

        oldest_review_date_in_batch = new_reviews_in_range[-1]['at']
        if oldest_review_date_in_batch < oldest_review_date_fetched:
            oldest_review_date_fetched = oldest_review_date_in_batch

        elapsed_seconds = (end_date - oldest_review_date_fetched).total_seconds()
        progress = min(max(elapsed_seconds / total_seconds, 0), 1)

        if progress_bar is not None and progress_text is not None:
            progress_bar.progress(progress)
            progress_text.write(f"**{app_name}: Fetched {total_reviews_fetched} reviews so far...** Progress: {progress*100:.2f}%")

        reviews_df = pd.DataFrame(new_reviews_in_range)
        reviews_df['app_name'] = app_name
        reviews_df['country'] = country
        reviews_df['language'] = language

        reviews_df = reviews_df.replace({pd.NaT: None})
        reviews_df = reviews_df.where(pd.notnull(reviews_df), None)

        reviews_df['at'] = pd.to_datetime(reviews_df['at']).dt.date

        datetime_fields = ['at', 'repliedAt']
        for field in datetime_fields:
            if field in reviews_df.columns:
                reviews_df[field] = reviews_df[field].apply(lambda x: x.isoformat() if x is not None else None)

        # Prepare the SQL statement
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
                row['at'],
                row.get('replyContent', None),
                row.get('repliedAt', None),
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
    
    if progress_bar is not None and progress_text is not None:
        progress_bar.progress(1.0)
        if st.session_state.get('stop_download'):
            progress_text.write(f"**Download stopped. Total reviews fetched: {total_reviews_fetched}.**")
        else:
            progress_text.write(f"**Finished downloading reviews for {app_name}. Total reviews fetched: {total_reviews_fetched}.**")