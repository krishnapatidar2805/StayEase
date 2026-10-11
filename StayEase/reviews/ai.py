"""
AI Feature #3: Review Sentiment Analysis
-----------------------------------------
Uses TextBlob (a lightweight NLP library built on NLTK) to compute the
polarity of a review's text and classify it as Positive / Neutral / Negative.

Polarity ranges from -1 (very negative) to +1 (very positive).
"""
try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None


def analyze_sentiment(text: str):
    """Return (label, polarity_score) for a piece of review text."""
    if not text or not text.strip():
        return 'neutral', 0.0

    if TextBlob:
        blob = TextBlob(text)
        polarity = round(blob.sentiment.polarity, 3)
    else:
        # Fallback simple sentiment scoring if textblob isn't installed
        positive_words = {'good', 'great', 'excellent', 'amazing', 'clean', 'nice', 'best', 'wonderful', 'love', 'comfortable', 'friendly', 'happy', 'superb'}
        negative_words = {'bad', 'dirty', 'poor', 'terrible', 'worst', 'horrible', 'noisy', 'rude', 'slow', 'hate', 'disappointed'}
        words = set(text.lower().split())
        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)
        if pos_count > neg_count:
            polarity = 0.5
        elif neg_count > pos_count:
            polarity = -0.5
        else:
            polarity = 0.0

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
