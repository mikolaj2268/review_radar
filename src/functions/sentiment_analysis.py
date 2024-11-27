# src/functions/sentiment_analysis.py

import nltk
nltk.download('vader_lexicon')  # Dla VADER
nltk.download('punkt')          # Dla TextBlob
nltk.download('averaged_perceptron_tagger')  # Dodatkowo dla TextBlob
nltk.download('wordnet')        # Dodatkowo dla TextBlob

from src.models.textblob_model import analyze_sentiment_textblob
from src.models.vader_model import analyze_sentiment_vader
from src.models.roberta_model import analyze_sentiment_roberta
from src.models.distilbert_model import analyze_sentiment_distilbert

def perform_sentiment_analysis(text, model_name):
    """
    Route the sentiment analysis to the appropriate model based on model_name.

    Args:
        text (str): Text content to analyze.
        model_name (str): Name of the model to use ('TextBlob', 'VADER', 'RoBERTa', 'DistilBERT').

    Returns:
        str: Sentiment label.
    """
    if model_name == 'TextBlob':
        return analyze_sentiment_textblob(text)
    elif model_name == 'VADER':
        return analyze_sentiment_vader(text)
    elif model_name == 'RoBERTa':
        return analyze_sentiment_roberta(text)
    elif model_name == 'DistilBERT':
        return analyze_sentiment_distilbert(text)
    else:
        return None