# src/models/vader_model.py

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Inicjalizacja analizatora VADER
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment_vader(text):
    try:
        score = analyzer.polarity_scores(text)
        compound = score['compound']
        if compound >= 0.05:
            return 'Positive'
        elif compound <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    except Exception:
        return 'Error'