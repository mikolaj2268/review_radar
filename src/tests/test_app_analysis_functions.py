# tests/test_app_analysis_functions.py

import unittest
import pandas as pd
import numpy as np
import datetime

from src.functions.app_analysis_functions import (
    preprocess_data,
    plot_score_distribution,
    generate_ngrams
)

class TestAppAnalysisFunctions(unittest.TestCase):
    def setUp(self):

        # Sample data for testing
        self.sample_data = pd.DataFrame({
            'content': [
                'This app is fantastic!',
                'I hate this app. It crashes frequently.',
                'Not bad, but could be better.',
                'Great app, very useful and intuitive.',
                'Terrible experience, it does not work at all.'
            ],
            'score': [5, 1, 3, 5, 1],
            'at': pd.date_range(start='2023-01-01', periods=5, freq='D'),
            'app_version': ['1.0', '1.1', '1.2', '1.3', '1.4'],
            'thumbs_up_count': [10, 5, 3, 20, 2]
        })

    def test_preprocess_data(self):
        """
        Test the preprocess_data function.
        """
        processed_data = preprocess_data(self.sample_data)

        # Check that the 'content' column has been lowercased and stripped
        expected_contents = [
            'this app is fantastic!',
            'i hate this app. it crashes frequently.',
            'not bad, but could be better.',
            'great app, very useful and intuitive.',
            'terrible experience, it does not work at all.'
        ]
        self.assertListEqual(
            processed_data['content'].tolist(),
            expected_contents,
            "The 'content' column should be lowercased and stripped."
        )

        # Ensure that 'content_length' is correctly calculated
        expected_lengths = self.sample_data['content'].str.len()
        pd.testing.assert_series_equal(
            processed_data['content_length'],
            expected_lengths,
            check_names=False,
            obj="Content lengths should match."
        )

        # Check that rows with 'score' outside 1-5 are removed (if any)
        self.assertTrue(
            processed_data['score'].between(1, 5).all(),
            "All scores should be between 1 and 5."
        )

        # Check that duplicates are removed
        self.assertEqual(
            len(processed_data),
            len(self.sample_data),
            "Duplicates should be removed."
        )

    def test_generate_ngrams(self):
        """
        Test the generate_ngrams function.
        """
        text = "This is a test. This test is only a test."
        n = 2
        ngrams = generate_ngrams(text, n)
        expected_ngrams = [
            'This is', 'is a', 'a test.', 'test. This',
            'This test', 'test is', 'is only', 'only a', 'a test.'
        ]
        self.assertEqual(
            ngrams,
            expected_ngrams,
            f"Generated {n}-grams should match the expected output."
        )

    def test_generate_ngrams_single_word(self):
        """
        Test generate_ngrams with ngram_length=1.
        """
        text = "Quick brown fox"
        n = 1
        ngrams = generate_ngrams(text, n)
        expected_ngrams = ['Quick', 'brown', 'fox']
        self.assertEqual(
            ngrams,
            expected_ngrams,
            "Generated unigrams should match the expected output."
        )

    def test_generate_ngrams_empty_string(self):
        """
        Test generate_ngrams with an empty string.
        """
        text = ""
        n = 2
        ngrams = generate_ngrams(text, n)
        expected_ngrams = []
        self.assertEqual(
            ngrams,
            expected_ngrams,
            "Generated ngrams from an empty string should be an empty list."
        )

    def test_plot_score_distribution(self):
        """
        Test the plot_score_distribution function.
        """
        fig = plot_score_distribution(self.sample_data)
        self.assertIsNotNone(fig, "Plot should not be None.")
        self.assertTrue(hasattr(fig, 'to_html'), "Plotly figure should have 'to_html' method.")

if __name__ == '__main__':
    unittest.main()