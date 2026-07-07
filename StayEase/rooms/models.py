from django.db import models
from django.urls import reverse


class RoomCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-door-open', help_text='Bootstrap icon class')

    class Meta:
        verbose_name_plural = 'Room Categories'

    def __str__(self):
        return self.name


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='bi-check-circle')

    class Meta:
        verbose_name_plural = 'Amenities'

    def __str__(self):
        return self.name


class Room(models.Model):
    PURPOSE_CHOICES = [
        ('business', 'Business Trip'),
        ('family', 'Family Vacation'),
        ('couple', 'Couple / Honeymoon'),
        ('solo', 'Solo Traveller'),
        ('friends', 'Friends Getaway'),
    ]

    name = models.CharField(max_length=150)
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name='rooms')
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=2, help_text='Max guests')
    beds = models.PositiveIntegerField(default=1)
    size_sqft = models.PositiveIntegerField(default=250)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='rooms')
    best_for = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='family')
    thumbnail = models.ImageField(upload_to='rooms/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    total_units = models.PositiveIntegerField(default=5)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('rooms:detail', kwargs={'pk': self.pk})

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(agg, 1) if agg else self.rating

    @property
    def tone_class(self):
        """Deterministic color tone (tone-0..tone-5) used for the room banner."""
        return f"tone-{self.id % 6}"

    @property
    def icon_class(self):
        icons = ['bi-door-open', 'bi-house-heart', 'bi-building', 'bi-stars', 'bi-gem', 'bi-moon-stars']
        return icons[self.id % len(icons)]

    @property
    def tone_image(self):
        """Static path to this room's illustrated banner image."""
        return f"img/room-tone-{self.id % 6}.svg"


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/gallery/')
    caption = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.room.name} image"


class Wishlist(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='wishlist')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'room')

    def __str__(self):
        return f"{self.user.username} - {self.room.name}"
