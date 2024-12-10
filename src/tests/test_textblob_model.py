# tests/test_textblob_model.py

import unittest
from src.models.textblob_model import analyze_sentiment_textblob

class TestTextBlobModel(unittest.TestCase):
    def test_analyze_sentiment_textblob_positive(self):
        """
        Test the analyze_sentiment_textblob function with positive sentiment.
        """
        text = "I love this app, it's fantastic!"
        result = analyze_sentiment_textblob(text)
        expected_result = {
            'textblob_sentiment_label': 'Positive',
            'textblob_polarity': 0.5
        }
        self.assertEqual(result, expected_result, "Should correctly identify positive sentiment.")

    def test_analyze_sentiment_textblob_negative(self):
        """
        Test the analyze_sentiment_textblob function with negative sentiment.
        """
        text = "This app is terrible and I hate it."
        result = analyze_sentiment_textblob(text)
        
        # Assert that the sentiment label is 'Negative'
        self.assertEqual(result.get('textblob_sentiment_label'), 'Negative', "Should correctly identify negative sentiment.")
        
        # Assert that the polarity is negative
        self.assertLess(result.get('textblob_polarity', 0), 0, "Polarity should be negative.")

    def test_analyze_sentiment_textblob_error(self):
        """
        Test the analyze_sentiment_textblob function handling errors.
        """
        text = None  # Passing None to cause an exception
        result = analyze_sentiment_textblob(text)
        expected_result = {
            'textblob_sentiment_label': 'Error',
            'textblob_polarity': None
        }
        self.assertEqual(result, expected_result, "Should handle exceptions and return error state.")

if __name__ == '__main__':
    unittest.main()