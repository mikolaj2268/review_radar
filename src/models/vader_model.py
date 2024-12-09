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
            'vader_pos': pos,
            'vader_neu': neu,
            'vader_neg': neg,
            'vader_compound': compound
        }
    except Exception:
        return {
            'vader_sentiment_label': 'Error',
            'vader_pos': None,
            'vader_neu': None,
            'vader_neg': None,
            'vader_compound': None
        }