# scraper.py

import pandas as pd
from google_play_scraper import Sort, reviews, search
from datetime import datetime, timedelta

def select_app(app_name):
    """Searches for apps matching the input name and returns a list of options."""
    try:
        search_results = search(app_name, n_hits=5, lang='en', country='us')
        return search_results
    except Exception as e:
        return []

def scrape_and_store_reviews(app_name, app_id, conn, progress_placeholder=None, start_date=None, end_date=None, country='us', language='en'):
    """Scrapes reviews and stores them in the PostgreSQL database."""
    cursor = conn.cursor()

    # If dates are not provided, get the latest date from the database
    if not start_date:
        cursor.execute("""
            SELECT MAX(at) FROM app_reviews WHERE app_name = %s;
        """, (app_name,))
        result = cursor.fetchone()
        if result[0]:
            start_date = result[0]
        else:
            start_date = datetime.now() - timedelta(days=7)
    if not end_date:
        end_date = datetime.now()

    original_start_date = start_date  # Keep the original start date for reporting
    original_end_date = end_date      # Keep the original end date for reporting

    total_reviews_fetched = 0
    all_reviews = []
    continuation_token = None

    # Display initial message with start date
    if progress_placeholder is not None:
        progress_placeholder.write(f"**Starting to download reviews for {app_name} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...**")

    # Fetch reviews until there are no more continuation tokens
    while True:
        new_reviews, continuation_token = reviews(
            app_id,
            lang=language,
            country=country,
            sort=Sort.NEWEST,
            count=200,
            continuation_token=continuation_token
        )

        if not new_reviews:
            break

        # Filter reviews within the date range
        filtered_new_reviews = [
            review for review in new_reviews
            if start_date < review['at'] <= end_date
        ]

        if not filtered_new_reviews:
            break

        all_reviews.extend(filtered_new_reviews)
        total_reviews_fetched += len(filtered_new_reviews)

        # Update progress message
        if progress_placeholder is not None:
            progress_placeholder.write(f"**{app_name}: Fetched {total_reviews_fetched} reviews so far...**")

        # Check if the oldest review fetched is older than the start_date
        oldest_review_date = filtered_new_reviews[-1]['at']
        if oldest_review_date <= start_date:
            break

        if continuation_token is None:
            break

    if not all_reviews:
        if progress_placeholder is not None:
            progress_placeholder.write(f"**No new reviews found for {app_name}.**")
        cursor.close()
        return total_reviews_fetched, original_start_date, original_end_date

    # Insert data into PostgreSQL
    reviews_df = pd.DataFrame(all_reviews)
    reviews_df['app_name'] = app_name
    reviews_df['country'] = country
    reviews_df['language'] = language

    # Replace NaT and NaN values with None
    reviews_df = reviews_df.replace({pd.NaT: None})
    reviews_df = reviews_df.where(pd.notnull(reviews_df), None)

    for _, row in reviews_df.iterrows():
        cursor.execute('''
            INSERT INTO app_reviews (
                review_id, user_name, user_image, content, score, thumbs_up_count,
                review_created_version, at, reply_content, replied_at, app_version,
                app_name, country, language
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (review_id) DO NOTHING;
        ''', (
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
    cursor.close()

    # Final progress message
    if progress_placeholder is not None:
        progress_placeholder.write(f"**Finished downloading reviews for {app_name}. Total new reviews fetched: {total_reviews_fetched}.**")

    return total_reviews_fetched, original_start_date, original_end_date
