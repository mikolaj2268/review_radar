# src/models/vader_model.py

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment_vader(text):
    try:
        score = analyzer.polarity_scores(text)
        compound = float(score['compound'])
        pos = float(score['pos'])
        neu = float(score['neu'])
        neg = float(score['neg'])

        if compound >= 0.05:
            label = 'Positive'
        elif compound <= -0.05:
            label = 'Negative'
        else:
            label = 'Neutral'
        
        return {
            'vader_sentiment_label': label,
            'vader_positive': pos,
            'vader_neutral': neu,
            'vader_negative': neg,
            'vader_compound': compound
        }
    except Exception:
        return {
            'vader_sentiment_label': 'Error',
            'vader_positive': None,
            'vader_neutral': None,
            'vader_negative': None,
            'vader_compound': None
        }