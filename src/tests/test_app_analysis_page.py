# tests/test_app_analysis_page.py

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import datetime

# Import the module and functions to test
from src.pages.app_analysis_page import (
    app_analysis_page,
    display_reviews,
    preprocess_data
)

class TestAppAnalysisPage(unittest.TestCase):
    def setUp(self):

        # Sample DataFrame for testing
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

    @patch('src.pages.app_analysis_page.search_and_select_app')
    @patch('src.pages.app_analysis_page.display_reviews')
    @patch('src.pages.app_analysis_page.create_tables')
    @patch('src.pages.app_analysis_page.get_db_connection')
    @patch('src.pages.app_analysis_page.st')
    def test_app_analysis_page_runs(
        self,
        mock_st,                    
        mock_get_db_connection,       
        mock_create_tables,            
        mock_display_reviews,       
        mock_search_and_select_app    
    ):
        """
        Test that app_analysis_page function can be called without errors.
        """
        # Mock the database connection
        mock_conn = MagicMock()
        mock_get_db_connection.return_value = mock_conn

        # Mock the display_reviews function to return sample reviews
        mock_display_reviews.return_value = self.sample_reviews

        # Mock the search_and_select_app function to return a list with 'TestApp (ID: test123)'
        mock_search_and_select_app.return_value = [
            {'title': 'TestApp', 'appId': 'test123', 'icon': 'testapp_icon.png'}
        ]

        # Mock Streamlit sidebar inputs
        mock_st.sidebar.text_input.return_value = 'TestApp'
        mock_st.sidebar.selectbox.return_value = 'TestApp (ID: test123)'
        mock_st.button.return_value = True  # Simulate button press

        # Mock date_input to return specific dates for start and end
        mock_st.date_input.side_effect = [
            datetime.date(2023, 11, 1),  
            datetime.date(2023, 11, 30)
        ]

        # Initialize st.session_state as a MagicMock
        mock_st.session_state = MagicMock()

        # Internal storage for session state
        session_state_storage = {}

        # Define side effects for get and set operations
        def session_state_getitem(key):
            return session_state_storage.get(key, None)

        def session_state_setitem(key, value):
            session_state_storage[key] = value

        def session_state_get(key, default=None):
            return session_state_storage.get(key, default)

        # Set side effects on the mock session_state
        mock_st.session_state.__getitem__.side_effect = session_state_getitem
        mock_st.session_state.__setitem__.side_effect = session_state_setitem
        mock_st.session_state.get.side_effect = session_state_get

        try:
            app_analysis_page()
            success = True
        except Exception as e:
            success = False
            print(f"Error running app_analysis_page: {e}")

        self.assertTrue(success, "app_analysis_page should run without errors")

    @patch('src.pages.app_analysis_page.st')  # Patch Streamlit
    def test_preprocess_data(self, mock_st):
        """
        Test the preprocess_data function within app_analysis_page.
        """
       
        processed_data = preprocess_data(self.sample_reviews)

        # Check that 'content_length' is added
        self.assertIn('content_length', processed_data.columns, "'content_length' should be added to the DataFrame.")

        # Check that 'content_length' values are correct
        expected_lengths = self.sample_reviews['content'].str.len()
        pd.testing.assert_series_equal(
            processed_data['content_length'],
            expected_lengths,
            check_names=False,
            obj="Content lengths should match."
        )

if __name__ == '__main__':
    unittest.main()