import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rooms.models import RoomCategory, Amenity, Room
from reviews.models import Review


CATEGORIES = [
    ("Standard Room", "bi-door-open", "Comfortable and cozy, perfect for solo travellers or short stays."),
    ("Deluxe Room", "bi-house-heart", "Spacious rooms with premium furnishings and a scenic view."),
    ("Executive Suite", "bi-building", "Ideal for business travellers, with a private workspace."),
    ("Family Suite", "bi-people-fill", "Extra space and beds designed for families and groups."),
    ("Honeymoon Suite", "bi-heart", "Romantic decor with a private balcony for couples."),
    ("Presidential Suite", "bi-gem", "Our most luxurious offering with full concierge service."),
]

AMENITIES = [
    ("Free WiFi", "bi-wifi"), ("Air Conditioning", "bi-snow"), ("Breakfast Included", "bi-cup-hot"),
    ("Swimming Pool", "bi-water"), ("Free Parking", "bi-p-square"), ("Gym Access", "bi-bicycle"),
    ("Room Service", "bi-bell"), ("Mini Bar", "bi-cup-straw"), ("Balcony View", "bi-binoculars"),
    ("Smart TV", "bi-tv"),
]

ROOM_NAMES = [
    "Ocean Breeze", "Sunset View", "Royal Comfort", "Garden Retreat", "Skyline Escape",
    "Golden Horizon", "Serenity Nook", "Urban Loft", "Moonlight Chamber", "Palm Grove",
    "Emerald Hideaway", "Amber Court", "Crystal Bay", "Maple Suite", "Lotus Pavilion",
    "Coral Reef Room", "Willow Lodge", "Starlight Room", "Cedar Haven", "Ivory Terrace",
]

REVIEW_TEXTS = [
    ("Absolutely loved our stay! The room was spotless and the staff were incredibly friendly.", 5),
    ("Great value for money, comfortable bed and quick check-in process.", 4),
    ("The room was okay, nothing special but got the job done for one night.", 3),
    ("Wifi was patchy and the AC made a lot of noise. Disappointed with the experience.", 2),
    ("Terrible experience, room was not clean and staff was rude at check-in.", 1),
    ("Wonderful view from the balcony, would definitely book again!", 5),
    ("Decent stay overall, breakfast could have had more variety.", 3),
    ("Loved the spa access and the extremely comfortable mattress.", 5),
    ("Booking process was smooth but the room smelled a bit musty.", 2),
    ("Perfect for our honeymoon, the staff even decorated the room for us!", 5),
]


class Command(BaseCommand):
    help = 'Seed the database with demo hotel data (categories, amenities, rooms, users, reviews).'

    def handle(self, *args, **options):
        self.stdout.write('Seeding StayEase demo data...')

        # --- Categories ---
        categories = []
        for name, icon, desc in CATEGORIES:
            cat, _ = RoomCategory.objects.get_or_create(name=name, defaults={'icon': icon, 'description': desc})
            categories.append(cat)

        # --- Amenities ---
        amenities = []
        for name, icon in AMENITIES:
            a, _ = Amenity.objects.get_or_create(name=name, defaults={'icon': icon})
            amenities.append(a)

        # --- Superuser ---
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@stayease.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser -> username: admin / password: admin123'))
        else:
            admin = User.objects.get(username='admin')

        # --- Demo customer ---
        if not User.objects.filter(username='demo_guest').exists():
            demo = User.objects.create_user('demo_guest', 'guest@stayease.com', 'guest12345',
                                             first_name='Riya', last_name='Sharma')
            demo.profile.is_email_verified = True
            demo.profile.save()
            self.stdout.write(self.style.SUCCESS('Created demo customer -> username: demo_guest / password: guest12345'))
        else:
            demo = User.objects.get(username='demo_guest')

        purposes = [c[0] for c in Room.PURPOSE_CHOICES]

        # --- Rooms ---
        created_rooms = []
        for i, name in enumerate(ROOM_NAMES):
            cat = categories[i % len(categories)]
            price = random.choice([1500, 2000, 2500, 3200, 4000, 5500, 7000, 9500, 12000])
            room, created = Room.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'description': f"The {name} room offers a blend of comfort and style, part of our {cat.name} collection. "
                                    f"Enjoy a relaxing stay with thoughtfully designed interiors and attentive service.",
                    'price_per_night': price,
                    'capacity': random.choice([1, 2, 2, 3, 4, 6]),
                    'beds': random.choice([1, 1, 2, 3]),
                    'size_sqft': random.choice([180, 220, 280, 350, 450, 600]),
                    'best_for': random.choice(purposes),
                    'total_units': random.randint(2, 8),
                    'rating': round(random.uniform(3.6, 5.0), 1),
                }
            )
            if created:
                room.amenities.set(random.sample(amenities, k=random.randint(3, 6)))
            created_rooms.append(room)

        self.stdout.write(self.style.SUCCESS(f'{len(created_rooms)} rooms ready.'))

        # --- Reviews ---
        review_count = 0
        for room in created_rooms:
            if room.reviews.exists():
                continue
            for text, rating in random.sample(REVIEW_TEXTS, k=random.randint(2, 4)):
                Review.objects.create(room=room, user=demo, rating=rating, comment=text)
                review_count += 1

        self.stdout.write(self.style.SUCCESS(f'{review_count} AI-analyzed reviews created.'))
        self.stdout.write(self.style.SUCCESS('Seeding complete! Run the server and log in as admin/demo_guest.'))
