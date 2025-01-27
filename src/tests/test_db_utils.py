import unittest
import sqlite3
import pandas as pd
import datetime

from src.database_connection.db_utils import (
    create_reviews_table,
    get_app_data,
    get_reviews_for_app,
    insert_reviews,
    get_reviews_date_ranges
)

class TestDBUtils(unittest.TestCase):
    def setUp(self):
        # Initialize SQLite database
        self.conn = sqlite3.connect(':memory:')
        create_reviews_table(self.conn)

        self.sample_reviews = pd.DataFrame({
            'review_id': ['1', '2', '3'],
            'user_name': ['User1', 'User2', 'User3'],
            'user_image': ['image1.png', 'image2.png', 'image3.png'],
            'content': ['Great app!', 'Not bad', 'Needs improvement'],
            'score': [5, 4, 2],
            'thumbs_up_count': [10, 5, 1],
            'review_created_version': ['1.0', '1.1', '1.2'],
            'at': [
                datetime.datetime(2023, 11, 1),
                datetime.datetime(2023, 11, 15),
                datetime.datetime(2023, 12, 1)
            ],
            'reply_content': [None, 'Thank you!', None],
            'replied_at': [None, datetime.datetime(2023, 11, 16), None],
            'app_version': ['1.0', '1.1', '1.2'],
            'app_name': ['TestApp', 'TestApp', 'TestApp'],
            'country': ['us', 'us', 'us'],
            'language': ['en', 'en', 'en']
        })

        insert_reviews(self.conn, self.sample_reviews)

    def tearDown(self):
        self.conn.close()

    def test_create_reviews_table_exists(self):
        """Test that the reviews table exists after creation."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_reviews';")
        table = cursor.fetchone()
        cursor.close()
        self.assertIsNotNone(table, "app_reviews table should exist.")
        self.assertEqual(table[0], 'app_reviews', "Table name should be 'app_reviews'.")

    def test_get_app_data(self):
        """Test fetching all data for a specific app."""
        retrieved_data = get_app_data(self.conn, 'TestApp')
        self.assertEqual(len(retrieved_data), 3)
        
        expected_contents = [
            'Needs improvement',
            'Not bad',
            'Great app!'
        ]
        self.assertListEqual(
            retrieved_data['content'].tolist(),
            expected_contents,
            "Data should be ordered by 'at' descending."
        )

    def test_get_app_data_with_no_reviews(self):
        """Test fetching data for an app with no reviews."""
        retrieved_data = get_app_data(self.conn, 'NonExistentApp')
        self.assertTrue(retrieved_data.empty, "Should return an empty DataFrame for an app with no reviews.")

    def test_get_reviews_for_app(self):
        """Test fetching reviews within a date range."""
        start_date = '2023-11-01'
        end_date = '2023-11-30'
        retrieved_data = get_reviews_for_app(self.conn, 'TestApp', start_date, end_date)
        self.assertEqual(len(retrieved_data), 2)
        expected_contents = ['Not bad', 'Great app!']
        self.assertListEqual(
            retrieved_data['content'].tolist(),
            expected_contents,
            "Should fetch reviews within the specified date range."
        )

    def test_get_reviews_date_ranges(self):
        """Test fetching distinct review dates for an app."""
        retrieved_dates = get_reviews_date_ranges(self.conn, 'TestApp')
        expected_dates = {'2023-11-01', '2023-11-15', '2023-12-01'}
        self.assertSetEqual(
            set(retrieved_dates),
            expected_dates,
            "Should return the correct set of distinct review dates."
        )

    def test_insert_reviews_duplicate(self):
        """Test that inserting duplicate reviews does not cause errors and duplicates are not added."""
        insert_reviews(self.conn, self.sample_reviews)
        retrieved_data = get_app_data(self.conn, 'TestApp')
        self.assertEqual(len(retrieved_data), 3, "Should still have 3 reviews, no duplicates added.")

    def test_insert_reviews_new(self):
        """Test inserting new reviews."""
        new_reviews = pd.DataFrame({
            'review_id': ['4'],
            'user_name': ['User4'],
            'user_image': ['image4.png'],
            'content': ['Excellent!'],
            'score': [5],
            'thumbs_up_count': [20],
            'review_created_version': ['1.3'],
            'at': [datetime.datetime(2023, 12, 5)],
            'reply_content': ['Thanks!'],
            'replied_at': [datetime.datetime(2023, 12, 6)],
            'app_version': ['1.3'],
            'app_name': ['TestApp'],
            'country': ['us'],
            'language': ['en']
        })
        insert_reviews(self.conn, new_reviews)
        retrieved_data = get_app_data(self.conn, 'TestApp')
        self.assertEqual(len(retrieved_data), 4, "Should have 4 reviews after inserting a new one.")
        self.assertIn('Excellent!', retrieved_data['content'].tolist(), "New review content should be present.")

if __name__ == '__main__':
    unittest.main()