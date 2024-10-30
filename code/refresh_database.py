import psycopg2
import pandas as pd
from google_play_scraper import Sort, reviews, search
from datetime import datetime, timedelta

# Function to get app ID based on its name
def get_app_id(app_name):
    try:
        search_results = search(app_name, n_hits=1, lang='en', country='us')
        if search_results:
            app_id = search_results[0]['appId']
            print(f"Found app: {search_results[0]['title']} (ID: {app_id})")
            return app_id
        else:
            print(f"No app found with the name '{app_name}'.")
            return None
    except Exception as e:
        print(f"Error searching for app '{app_name}': {e}")
        return None

# Helper function to clean values
def clean_value(val):
    if pd.isnull(val) or val is pd.NaT:
        return None
    else:
        return val

# Function to scrape reviews and store them in PostgreSQL
def scrape_and_store_reviews(app_name, app_id, conn, start_date=None, end_date=None, country='us', language='en'):
    # If dates are not provided, get the latest date from the database
    if not start_date:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(at) FROM app_reviews WHERE app_name = %s;
        """, (app_name,))
        result = cursor.fetchone()
        cursor.close()
        if result[0]:
            start_date = result[0]
            print(f"Latest date in the database for {app_name}: {start_date}")
        else:
            # If there are no reviews in the database, set default start date
            start_date = datetime.now() - timedelta(days=7)
            print(f"No reviews found in the database for {app_name}. Setting default start date: {start_date}")
    if not end_date:
        end_date = datetime.now()

    print(f"Scraping reviews for {app_name} ({app_id}) from {start_date} to {end_date}...\n")

    total_reviews_fetched = 0
    all_reviews = []
    continuation_token = None

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

        print(f"Fetched {len(filtered_new_reviews)} reviews. Total so far: {total_reviews_fetched}")

        # Check if the oldest review fetched is older than the start_date
        oldest_review_date = filtered_new_reviews[-1]['at']
        if oldest_review_date <= start_date:
            break

        if continuation_token is None:
            break

    if not all_reviews:
        print(f"No new reviews found for {app_name} in the specified date range.\n")
        return

    # Insert data into PostgreSQL
    reviews_df = pd.DataFrame(all_reviews)
    reviews_df['app_name'] = app_name
    reviews_df['country'] = country
    reviews_df['language'] = language

    # Replace NaT and NaN values with None
    reviews_df = reviews_df.replace({pd.NaT: None})
    reviews_df = reviews_df.where(pd.notnull(reviews_df), None)

    cursor = conn.cursor()
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
            clean_value(row['at']),
            row.get('replyContent', None),
            clean_value(row.get('repliedAt', None)),
            row.get('appVersion', None),
            app_name,
            country,
            language
        ))
    conn.commit()
    cursor.close()

    print(f"Successfully fetched and stored a total of {total_reviews_fetched} reviews for {app_name}.\n")

# Main function
def main():
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        database="google_play_reviews",
        user="postgres",
        password="password"
    )

    # Create table in the database if it doesn't exist
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_reviews (
            review_id VARCHAR(255) PRIMARY KEY,
            user_name VARCHAR(255),
            user_image TEXT,
            content TEXT,
            score INT,
            thumbs_up_count INT,
            review_created_version VARCHAR(50),
            at TIMESTAMP,
            reply_content TEXT,
            replied_at TIMESTAMP,
            app_version VARCHAR(50),
            app_name VARCHAR(255),
            country VARCHAR(10),
            language VARCHAR(10)
        );
    ''')
    conn.commit()
    cursor.close()

    # Get the list of distinct app names from the database
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT app_name FROM app_reviews;")
    apps_in_db = cursor.fetchall()
    cursor.close()

    if not apps_in_db:
        print("No apps found in the database to refresh.")
        conn.close()
        return

    # For each app, refresh the data
    for app_tuple in apps_in_db:
        app_name = app_tuple[0]
        print(f"\nProcessing app: {app_name}")
        app_id = get_app_id(app_name)
        if app_id:
            scrape_and_store_reviews(app_name, app_id, conn)
        else:
            print(f"Could not find app ID for {app_name}. Skipping.")

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
