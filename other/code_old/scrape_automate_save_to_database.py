import psycopg2
import pandas as pd
from google_play_scraper import Sort, reviews, search
from tqdm import tqdm
from datetime import datetime, timedelta

# List of apps to monitor
app_names = []  # You can modify this initial list if desired

# Function to get app ID based on its name and allow user to select from search results
def select_app(app_name):
    try:
        # Search for apps matching the input name
        search_results = search(app_name, n_hits=5, lang='en', country='us')
        if search_results:
            print(f"Search results for '{app_name}':")
            for idx, result in enumerate(search_results):
                print(f"{idx + 1}. {result['title']} (ID: {result['appId']})")
            # Ask the user to select the correct app
            while True:
                selection = input(f"Select the number of the app you want to add (1-{len(search_results)}), or '0' to cancel: ").strip()
                if selection.isdigit():
                    selection = int(selection)
                    if 1 <= selection <= len(search_results):
                        chosen_app = search_results[selection - 1]
                        print(f"Selected app: {chosen_app['title']} (ID: {chosen_app['appId']})")
                        return chosen_app['title'], chosen_app['appId']
                    elif selection == 0:
                        print("Cancelled adding app.")
                        return None, None
                print("Invalid selection. Please try again.")
        else:
            print(f"No apps found matching '{app_name}'.")
            return None, None
    except Exception as e:
        print(f"Error searching for apps matching '{app_name}': {e}")
        return None, None

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

    app_list = []  # List to store tuples of (app_name, app_id)

    # Display the list of apps
    print("The script will fetch reviews for the following apps:")
    for app in app_names:
        # Get the app ID
        app_name, app_id = select_app(app)
        if app_id:
            app_list.append((app_name, app_id))
        else:
            print(f"Skipping '{app}' as it was not found.")

    # Ask the user if they want to add more apps
    while True:
        add_app = input("Do you want to add another app to the list? (yes/no): ").strip().lower()
        if add_app == 'yes':
            new_app = input("Enter the name of the app to add: ").strip()
            if new_app:
                app_name, app_id = select_app(new_app)
                if app_id:
                    app_list.append((app_name, app_id))
                    print(f"Added '{app_name}' to the list.")
                else:
                    print(f"Could not add '{new_app}' as it was not found.")
            else:
                print("No app name entered. Please try again.")
        elif add_app == 'no':
            break
        else:
            print("Please answer 'yes' or 'no'.")

    # Confirm the final list of apps
    if not app_list:
        print("No valid apps were selected. Exiting.")
        conn.close()
        return

    print("\nThe script will fetch reviews for the following apps:")
    for idx, (app_name, app_id) in enumerate(app_list, start=1):
        print(f"{idx}. {app_name} (ID: {app_id})")

    while True:
        proceed = input("Do you accept this list and want to proceed? (yes/no): ").strip().lower()
        if proceed == 'yes':
            break
        elif proceed == 'no':
            print("Operation cancelled by the user. Exiting.")
            conn.close()
            return
        else:
            print("Please answer 'yes' or 'no'.")

    # Get date range from user or set defaults
    try:
        start_date_str = input("Enter start date (YYYY-MM-DD), leave blank to fetch from the latest date in the database: ").strip()
        end_date_str = input("Enter end date (YYYY-MM-DD), leave blank for today's date: ").strip()

        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        else:
            start_date = None  # Will be set in scrape_and_store_reviews

        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        else:
            end_date = None  # Will be set in scrape_and_store_reviews

    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        conn.close()
        return

    # Set country and language
    country = 'us'
    language = 'en'

    # Fetch reviews for all apps in the list
    for app_name, app_id in app_list:
        scrape_and_store_reviews(app_name, app_id, conn, start_date=start_date, end_date=end_date, country=country, language=language)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
