"""
AI Feature #3: Review Sentiment Analysis
-----------------------------------------
Uses TextBlob (a lightweight NLP library built on NLTK) to compute the
polarity of a review's text and classify it as Positive / Neutral / Negative.

Polarity ranges from -1 (very negative) to +1 (very positive).
"""
from textblob import TextBlob


def analyze_sentiment(text: str):
    """Return (label, polarity_score) for a piece of review text."""
    if not text or not text.strip():
        return 'neutral', 0.0

    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 3)

    if polarity > 0.15:
        label = 'positive'
    elif polarity < -0.15:
        label = 'negative'
    else:
        label = 'neutral'

    return label, polarity


def sentiment_summary(queryset):
    """Aggregate sentiment counts + percentages for a Review queryset."""
    total = queryset.count()
    if total == 0:
        return {'positive': 0, 'neutral': 0, 'negative': 0, 'total': 0,
                'positive_pct': 0, 'neutral_pct': 0, 'negative_pct': 0}

    positive = queryset.filter(sentiment='positive').count()
    neutral = queryset.filter(sentiment='neutral').count()
    negative = queryset.filter(sentiment='negative').count()

    return {
        'positive': positive, 'neutral': neutral, 'negative': negative, 'total': total,
        'positive_pct': round(positive / total * 100, 1),
        'neutral_pct': round(neutral / total * 100, 1),
        'negative_pct': round(negative / total * 100, 1),
    }
