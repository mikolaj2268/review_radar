import unittest
from unittest.mock import patch, MagicMock
import torch

from src.models.distilbert_model import analyze_sentiment_distilbert


class TestDistilBERTModel(unittest.TestCase):
    @patch('src.models.distilbert_model.model')
    @patch('src.models.distilbert_model.tokenizer')
    def test_analyze_sentiment_distilbert_positive(self, mock_tokenizer, mock_model):
        """
        Test the analyze_sentiment_distilbert function with positive sentiment.
        """
        
        mock_tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }

        
        mock_logits = torch.tensor([[-1.0, 1.0]]) 
        mock_outputs = MagicMock()
        mock_outputs.logits = mock_logits
        mock_model.return_value = mock_outputs

        text = "Absolutely fantastic! Highly recommend."
        result = analyze_sentiment_distilbert(text)

        expected_result = {
            'distilbert_sentiment_label': 'Positive',
            'distilbert_negative_prob': 0.1192,
            'distilbert_positive_prob': 0.8808
        }

        self.assertAlmostEqual(
            result['distilbert_negative_prob'],
            expected_result['distilbert_negative_prob'],
            places=4,
            msg="Negative probability should match expected value."
        )
        self.assertAlmostEqual(
            result['distilbert_positive_prob'],
            expected_result['distilbert_positive_prob'],
            places=4,
            msg="Positive probability should match expected value."
        )
        self.assertEqual(
            result['distilbert_sentiment_label'],
            expected_result['distilbert_sentiment_label'],
            "Sentiment label should be 'Positive'."
        )

    @patch('src.models.distilbert_model.model')
    @patch('src.models.distilbert_model.tokenizer')
    def test_analyze_sentiment_distilbert_negative(self, mock_tokenizer, mock_model):
        """
        Test the analyze_sentiment_distilbert function with negative sentiment.
        """
        mock_tokenizer.return_value = {
            'input_ids': torch.tensor([[4, 5, 6]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }

        mock_logits = torch.tensor([[1.0, -1.0]])
        mock_outputs = MagicMock()
        mock_outputs.logits = mock_logits
        mock_model.return_value = mock_outputs

        text = "Terrible experience. Will not use again."
        result = analyze_sentiment_distilbert(text)

        expected_result = {
            'distilbert_sentiment_label': 'Negative',
            'distilbert_negative_prob': 0.8808,
            'distilbert_positive_prob': 0.1192
        }

        self.assertAlmostEqual(
            result['distilbert_negative_prob'],
            expected_result['distilbert_negative_prob'],
            places=4,
            msg="Negative probability should match expected value."
        )
        self.assertAlmostEqual(
            result['distilbert_positive_prob'],
            expected_result['distilbert_positive_prob'],
            places=4,
            msg="Positive probability should match expected value."
        )
        self.assertEqual(
            result['distilbert_sentiment_label'],
            expected_result['distilbert_sentiment_label'],
            "Sentiment label should be 'Negative'."
        )


if __name__ == '__main__':
    unittest.main()