from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ('booking', 'New Booking'),
        ('payment', 'Payment Received'),
        ('review', 'New Review'),
        ('contact', 'Contact Message'),
    ]

    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='booking')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, help_text='Relative URL to send admin to on click')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.message

    @property
    def icon(self):
        return {
            'booking': 'bi-calendar-plus',
            'payment': 'bi-cash-coin',
            'review': 'bi-chat-quote',
            'contact': 'bi-envelope',
        }.get(self.notif_type, 'bi-bell')
