"""
AI Feature #1: Smart Room Recommendation Engine
AI Feature #4: Personalized Room Suggestions
-------------------------------------------------
A lightweight, explainable, rule + weighted-scoring based recommender.
No heavy ML training data is required (there usually isn't enough booking
history for a brand new hotel site to train a real model), but the scoring
approach mirrors how a content-based recommender system works: each room is
scored against the user's stated preferences across multiple weighted
features, then ranked.
"""
from decimal import Decimal
from django.db.models import Q
from .models import Room


def recommend_rooms(budget=None, guests=None, room_type=None, purpose=None, limit=6):
    """
    AI Smart Recommendation: score every available room against the
    customer's budget, guest count, preferred category and travel purpose.
    """
    rooms = Room.objects.filter(is_available=True).select_related('category')
    scored = []

    for room in rooms:
        score = 0.0
        reasons = []

        # --- Budget fit (heaviest weight - 40%) ---
        if budget:
            budget = Decimal(str(budget))
            if room.price_per_night <= budget:
                closeness = 1 - abs(float(budget - room.price_per_night)) / float(budget + 1)
                score += 40 * max(closeness, 0.3)
                reasons.append('Fits your budget')
            else:
                overage = float(room.price_per_night - budget) / float(budget)
                score += max(40 * (1 - overage), 0)

        # --- Guest capacity fit (25%) ---
        if guests:
            if room.capacity >= int(guests):
                score += 25 - min((room.capacity - int(guests)) * 3, 15)
                reasons.append(f'Sleeps up to {room.capacity} guests')
            else:
                score -= 20  # hard penalty, room too small

        # --- Room type / category match (20%) ---
        if room_type:
            if room_type.lower() in room.category.name.lower():
                score += 20
                reasons.append(f'Matches {room.category.name} preference')

        # --- Purpose of stay match (15%) ---
        if purpose:
            if room.best_for == purpose:
                score += 15
                reasons.append('Great for your trip purpose')

        # small boost for highly rated rooms
        score += float(room.average_rating) * 2

        scored.append((room, round(score, 1), reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def similar_rooms(room, limit=4):
    """
    AI Personalized Suggestion: find rooms similar to a given room, based on
    category, price range and best_for purpose (used on room detail pages
    and for 'because you booked X' suggestions).
    """
    price_low = room.price_per_night * Decimal('0.7')
    price_high = room.price_per_night * Decimal('1.3')

    qs = Room.objects.filter(is_available=True).exclude(pk=room.pk).filter(
        Q(category=room.category) | Q(best_for=room.best_for) |
        Q(price_per_night__gte=price_low, price_per_night__lte=price_high)
    ).distinct()[:limit]
    return qs


def personalized_suggestions_for_user(user, limit=4):
    """
    Look at a user's past bookings + wishlist to infer preferences, then
    recommend rooms similar to what they've shown interest in.
    """
    from bookings.models import Booking
    from .models import Wishlist

    past_room_ids = list(
        Booking.objects.filter(user=user).values_list('room_id', flat=True)
    ) + list(
        Wishlist.objects.filter(user=user).values_list('room_id', flat=True)
    )

    if not past_room_ids:
        # cold start: fall back to top rated rooms
        return Room.objects.filter(is_available=True).order_by('-rating')[:limit]

    categories = Room.objects.filter(id__in=past_room_ids).values_list('category_id', flat=True)
    purposes = Room.objects.filter(id__in=past_room_ids).values_list('best_for', flat=True)

    suggestions = Room.objects.filter(
        Q(category_id__in=categories) | Q(best_for__in=purposes),
        is_available=True,
    ).exclude(id__in=past_room_ids).distinct().order_by('-rating')[:limit]

    if suggestions.count() < limit:
        # top up with generally well-rated rooms
        extra = Room.objects.filter(is_available=True).exclude(
            id__in=list(suggestions.values_list('id', flat=True)) + past_room_ids
        ).order_by('-rating')[:limit - suggestions.count()]
        return list(suggestions) + list(extra)

    return suggestions
