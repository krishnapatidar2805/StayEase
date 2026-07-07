from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room


class Review(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, blank=True)
    sentiment_score = models.FloatField(default=0.0, help_text='Polarity score from -1 to 1')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} on {self.room.name}"

    def save(self, *args, **kwargs):
        # Run AI sentiment analysis automatically whenever a review is saved
        from reviews.ai import analyze_sentiment
        self.sentiment, self.sentiment_score = analyze_sentiment(self.comment)
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"
