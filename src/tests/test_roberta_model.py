import unittest
from unittest.mock import patch
import torch

from src.models.roberta_model import analyze_sentiment_roberta

class TestRoBERTaModel(unittest.TestCase):
    
    @patch('src.models.roberta_model.classifier')
    def test_analyze_sentiment_roberta_positive(self, mock_classifier):
        """
        Test the analyze_sentiment_roberta function with positive sentiment.
        """

        mock_classifier.return_value = [{'label': 'POSITIVE', 'score': 0.95}]
        
        text = "This app is wonderful! I love using it every day."
        result = analyze_sentiment_roberta(text)
        
        expected_label = 'Positive'
        
        self.assertEqual(result['roberta_sentiment_label'], expected_label)

    @patch('src.models.roberta_model.classifier')
    def test_analyze_sentiment_roberta_neutral(self, mock_classifier):
        """
        Test the analyze_sentiment_roberta function with neutral sentiment.
        """
        mock_classifier.return_value = [{'label': 'NEUTRAL', 'score': 0.80}]
        
        text = "The app functions adequately, neither outstanding nor terrible."
        result = analyze_sentiment_roberta(text)

        expected_label = 'Neutral'
        
        self.assertEqual(result['roberta_sentiment_label'], expected_label)

    @patch('src.models.roberta_model.classifier')
    def test_analyze_sentiment_roberta_negative(self, mock_classifier):
        """
        Test the analyze_sentiment_roberta function with negative sentiment.
        """
        mock_classifier.return_value = [{'label': 'NEGATIVE', 'score': 0.90}]
        
        text = "This app is terrible. It crashes every time I use it."
        result = analyze_sentiment_roberta(text)
        
        expected_label = 'Negative'
        
        self.assertEqual(result['roberta_sentiment_label'], expected_label)

    @patch('src.models.roberta_model.classifier')
    def test_analyze_sentiment_roberta_error(self, mock_classifier):
        """
        Test the analyze_sentiment_roberta function handling errors.
        """
        mock_classifier.side_effect = RuntimeError("Model error")
        
        text = "This should cause an error."
        result = analyze_sentiment_roberta(text)
        
        expected_result = {
            'roberta_sentiment_label': 'Error',
            'roberta_negative_prob': None,
            'roberta_neutral_prob': None,
            'roberta_positive_prob': None
        }

        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()