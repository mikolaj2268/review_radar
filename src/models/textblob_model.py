# src/models/textblob_model.py

from textblob import TextBlob

def analyze_sentiment_textblob(text):
    try:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        if polarity > 0:
            return 'Positive'
        elif polarity == 0:
            return 'Neutral'
        else:
            return 'Negative'
    except Exception:
        return 'Error'