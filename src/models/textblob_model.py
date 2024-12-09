# src/models/textblob_model.py

from textblob import TextBlob

def analyze_sentiment_textblob(text):
    try:
        analysis = TextBlob(text)
        polarity = float(analysis.sentiment.polarity)
        if polarity > 0:
            label = 'Positive'
        elif polarity == 0:
            label = 'Neutral'
        else:
            label = 'Negative'
        return {
            'textblob_sentiment_label': label,
            'textblob_polarity': polarity
        }
    except Exception:
        return {
            'textblob_sentiment_label': 'Error',
            'textblob_polarity': None
        }