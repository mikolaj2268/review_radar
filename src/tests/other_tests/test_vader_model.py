# # tests/test_vader_model.py

# import unittest
# from unittest.mock import patch
# from src.models.vader_model import analyze_sentiment_vader

# class TestVaderModel(unittest.TestCase):
#     @patch('src.models.vader_model.analyzer')
#     def test_analyze_sentiment_vader_positive(self, mock_analyzer):
#         """
#         Test the analyze_sentiment_vader function with positive sentiment.
#         """
#         # Mock analyzer behavior
#         mock_analyzer.polarity_scores.return_value = {
#             'neg': 0.0,
#             'neu': 0.5,
#             'pos': 0.5,
#             'compound': 0.6
#         }

#         text = "This app is amazing and works flawlessly!"
#         result = analyze_sentiment_vader(text)

#         expected_result = {
#             'vader_sentiment_label': 'Positive',
#             'vader_pos': 0.5,
#             'vader_neu': 0.5,
#             'vader_neg': 0.0,
#             'vader_compound': 0.6
#         }

#         self.assertEqual(result, expected_result, "Should correctly identify positive sentiment.")

#     @patch('src.models.vader_model.analyzer')
#     def test_analyze_sentiment_vader_negative(self, mock_analyzer):
#         """
#         Test the analyze_sentiment_vader function with negative sentiment.
#         """
#         # Mock analyzer behavior
#         mock_analyzer.polarity_scores.return_value = {
#             'neg': 0.6,
#             'neu': 0.3,
#             'pos': 0.1,
#             'compound': -0.7
#         }

#         text = "This app is terrible and crashes often."
#         result = analyze_sentiment_vader(text)

#         expected_result = {
#             'vader_sentiment_label': 'Negative',
#             'vader_pos': 0.1,
#             'vader_neu': 0.3,
#             'vader_neg': 0.6,
#             'vader_compound': -0.7
#         }

#         self.assertEqual(result, expected_result, "Should correctly identify negative sentiment.")

#     @patch('src.models.vader_model.analyzer')
#     def test_analyze_sentiment_vader_neutral(self, mock_analyzer):
#         """
#         Test the analyze_sentiment_vader function with neutral sentiment.
#         """
#         # Mock analyzer behavior
#         mock_analyzer.polarity_scores.return_value = {
#             'neg': 0.2,
#             'neu': 0.6,
#             'pos': 0.2,
#             'compound': 0.0
#         }

#         text = "This app is okay, neither good nor bad."
#         result = analyze_sentiment_vader(text)

#         expected_result = {
#             'vader_sentiment_label': 'Neutral',
#             'vader_pos': 0.2,
#             'vader_neu': 0.6,
#             'vader_neg': 0.2,
#             'vader_compound': 0.0
#         }

#         self.assertEqual(result, expected_result, "Should correctly identify neutral sentiment.")

#     @patch('src.models.vader_model.analyzer')
#     def test_analyze_sentiment_vader_error(self, mock_analyzer):
#         """
#         Test the analyze_sentiment_vader function handling errors.
#         """
#         # Mock analyzer to raise an exception
#         mock_analyzer.polarity_scores.side_effect = Exception("Analyzer error")

#         text = "This should cause an error."
#         result = analyze_sentiment_vader(text)

#         expected_result = {
#             'vader_sentiment_label': 'Error',
#             'vader_pos': None,
#             'vader_neu': None,
#             'vader_neg': None,
#             'vader_compound': None
#         }

#         self.assertEqual(result, expected_result, "Should handle exceptions and return error state.")

# if __name__ == '__main__':
#     unittest.main()