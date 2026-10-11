from django.db import models
from django.urls import reverse

try:
    from PIL import Image
    _ImageField = models.ImageField
except ImportError:
    _ImageField = models.FileField


class RoomCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-door-open', help_text='Bootstrap icon class')

    class Meta:
        verbose_name_plural = 'Room Categories'

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        category_photos = {
            'Standard Room': 'https://images.unsplash.com/photo-1595576508898-0ad5c879a061?auto=format&fit=crop&w=800&q=80',
            'Deluxe Room': 'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80',
            'Executive Suite': 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=800&q=80',
            'Family Suite': 'https://images.unsplash.com/photo-1598928506311-c55ded91a20c?auto=format&fit=crop&w=800&q=80',
            'Honeymoon Suite': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80',
            'Presidential Suite': 'https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=800&q=80',
        }
        return category_photos.get(self.name, 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80')



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
    thumbnail = _ImageField(upload_to='rooms/', blank=True, null=True)
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

    @property
    def image_url(self):
        """Returns uploaded thumbnail, or curated real high-definition hotel photo."""
        if self.thumbnail:
            try:
                return self.thumbnail.url
            except Exception:
                pass

        real_photos = [
            "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80",  # Ocean luxury suite
            "https://images.unsplash.com/photo-1591088398332-8a7791972843?auto=format&fit=crop&w=1200&q=80",  # Sunset warm suite
            "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=1200&q=80",  # Royal master suite
            "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&q=80",  # Modern elegant king room
            "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=1200&q=80",  # Boutique cozy haven
            "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=1200&q=80",  # Executive business suite
            "https://images.unsplash.com/photo-1595576508898-0ad5c879a061?auto=format&fit=crop&w=1200&q=80",  # Serene minimal bedroom
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80",  # Urban loft design
            "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=1200&q=80",  # Luxury ambient suite
            "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?auto=format&fit=crop&w=1200&q=80",  # Resort wooden villa
            "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=1200&q=80",  # Contemporary grand room
            "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?auto=format&fit=crop&w=1200&q=80",  # Family twin suite
            "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&q=80",  # Beachfront resort room
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80",  # City penthouse view
            "https://images.unsplash.com/photo-1540518614846-7ede433c4b42?auto=format&fit=crop&w=1200&q=80",  # Minimalist sanctuary
            "https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=1200&q=80",  # Tropical paradise villa
            "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?auto=format&fit=crop&w=1200&q=80",  # Mountain lodge room
            "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1200&q=80",  # Grand palace suite
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",  # Architectural luxury suite
            "https://images.unsplash.com/photo-1576671081837-49000212a370?auto=format&fit=crop&w=1200&q=80",  # Terrace luxury room
        ]
        return real_photos[self.id % len(real_photos)]

    @property
    def gallery_photos(self):
        """Returns uploaded gallery images or a curated set of real room photos."""
        if self.images.exists():
            return [img.image.url for img in self.images.all()]
        base_idx = self.id % 20
        pool = [
            "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1591088398332-8a7791972843?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1595576508898-0ad5c879a061?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?auto=format&fit=crop&w=1200&q=80",
        ]
        return [
            pool[base_idx % len(pool)],
            pool[(base_idx + 3) % len(pool)],
            pool[(base_idx + 6) % len(pool)],
        ]



class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = _ImageField(upload_to='rooms/gallery/')
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
