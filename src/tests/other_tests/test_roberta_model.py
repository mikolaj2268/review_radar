# # src/tests/other_tests/test_roberta_model.py

# import unittest
# from unittest.mock import patch
# import torch

# # Import the function to test
# from src.models.roberta_model import analyze_sentiment_roberta

# class TestRoBERTaModel(unittest.TestCase):
    
#     @patch('src.models.roberta_model.classifier')
#     def test_analyze_sentiment_roberta_positive(self, mock_classifier):
#         """
#         Test the analyze_sentiment_roberta function with positive sentiment.
#         """
#         # Mock the classifier's return value
#         mock_classifier.return_value = [{'label': 'POSITIVE', 'score': 0.95}]
        
#         # Input text with positive sentiment
#         text = "This app is wonderful! I love using it every day."
#         result = analyze_sentiment_roberta(text)
        
#         # Expected result
#         expected_label = 'Positive'
        
#         # Assertion for sentiment label
#         self.assertEqual(result['roberta_sentiment_label'], expected_label)

#     @patch('src.models.roberta_model.classifier')
#     def test_analyze_sentiment_roberta_neutral(self, mock_classifier):
#         """
#         Test the analyze_sentiment_roberta function with neutral sentiment.
#         """
#         # Mock the classifier's return value
#         mock_classifier.return_value = [{'label': 'NEUTRAL', 'score': 0.80}]
        
#         # Input text with neutral sentiment
#         text = "The app functions adequately, neither outstanding nor terrible."
#         result = analyze_sentiment_roberta(text)
        
#         # Expected result
#         expected_label = 'Neutral'
        
#         # Assertion for sentiment label
#         self.assertEqual(result['roberta_sentiment_label'], expected_label)

#     @patch('src.models.roberta_model.classifier')
#     def test_analyze_sentiment_roberta_negative(self, mock_classifier):
#         """
#         Test the analyze_sentiment_roberta function with negative sentiment.
#         """
#         # Mock the classifier's return value
#         mock_classifier.return_value = [{'label': 'NEGATIVE', 'score': 0.90}]
        
#         # Input text with negative sentiment
#         text = "This app is terrible. It crashes every time I use it."
#         result = analyze_sentiment_roberta(text)
        
#         # Expected result
#         expected_label = 'Negative'
        
#         # Assertion for sentiment label
#         self.assertEqual(result['roberta_sentiment_label'], expected_label)

#     @patch('src.models.roberta_model.classifier')
#     def test_analyze_sentiment_roberta_error(self, mock_classifier):
#         """
#         Test the analyze_sentiment_roberta function handling errors.
#         """
#         # Mock classifier to raise an exception when called
#         mock_classifier.side_effect = RuntimeError("Model error")
        
#         # Input text that triggers an error
#         text = "This should cause an error."
#         result = analyze_sentiment_roberta(text)
        
#         # Expected result in case of error
#         expected_result = {
#             'roberta_sentiment_label': 'Error',
#             'roberta_negative_prob': None,
#             'roberta_neutral_prob': None,
#             'roberta_positive_prob': None
#         }
        
#         # Assertion for error handling
#         self.assertEqual(result, expected_result)

# if __name__ == '__main__':
#     unittest.main()