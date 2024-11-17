import sqlite3

# Path for the new database
new_db_path = "google_play_reviews_empty.db"

# SQL statement to create the app_reviews table
create_table_query = """
CREATE TABLE IF NOT EXISTS app_reviews (
    review_id TEXT PRIMARY KEY,
    user_name TEXT,
    user_image TEXT,
    content TEXT,
    score INTEGER,
    thumbs_up_count INTEGER,
    review_created_version TEXT,
    at TIMESTAMP,
    reply_content TEXT,
    replied_at TIMESTAMP,
    app_version TEXT,
    app_name TEXT,
    country TEXT,
    language TEXT
);
"""

# Create the new database and table
def create_empty_database(db_path, create_query):
    # Connect to the new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute the query to create the table
    cursor.execute(create_query)

    # Commit and close the connection
    conn.commit()
    conn.close()

    print(f"Empty database created at: {db_path}")

# Run the function to create the empty database
create_empty_database(new_db_path, create_table_query)