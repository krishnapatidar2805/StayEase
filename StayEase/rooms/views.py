from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Room, RoomCategory, Amenity, Wishlist
from .ai import recommend_rooms, similar_rooms
from reviews.models import Review
from reviews.ai import sentiment_summary


def room_list_view(request):
    rooms = Room.objects.filter(is_available=True).select_related('category')

    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    capacity = request.GET.get('capacity', '')
    amenity = request.GET.get('amenity', '')
    sort = request.GET.get('sort', '')

    if query:
        rooms = rooms.filter(name__icontains=query)
    if category:
        rooms = rooms.filter(category_id=category)
    if min_price:
        rooms = rooms.filter(price_per_night__gte=min_price)
    if max_price:
        rooms = rooms.filter(price_per_night__lte=max_price)
    if capacity:
        rooms = rooms.filter(capacity__gte=capacity)
    if amenity:
        rooms = rooms.filter(amenities__id=amenity)

    if sort == 'price_low':
        rooms = rooms.order_by('price_per_night')
    elif sort == 'price_high':
        rooms = rooms.order_by('-price_per_night')
    elif sort == 'rating':
        rooms = rooms.order_by('-rating')
    else:
        rooms = rooms.order_by('-created_at')

    rooms = rooms.distinct()
    paginator = Paginator(rooms, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'categories': RoomCategory.objects.all(),
        'amenities': Amenity.objects.all(),
        'query': query,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'capacity': capacity,
        'amenity': amenity,
        'sort': sort,
    }
    return render(request, 'rooms/room_list.html', context)


def room_detail_view(request, pk):
    room = get_object_or_404(Room, pk=pk)
    reviews = room.reviews.select_related('user').all()
    similar = similar_rooms(room)
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, room=room).exists()

    context = {
        'room': room,
        'reviews': reviews,
        'similar_rooms': similar,
        'is_wishlisted': is_wishlisted,
        'sentiment_stats': sentiment_summary(reviews),
    }
    return render(request, 'rooms/room_detail.html', context)


def recommend_view(request):
    """AI Smart Room Recommendation form + results page."""
    results = None
    if request.GET.get('submitted'):
        budget = request.GET.get('budget') or None
        guests = request.GET.get('guests') or None
        room_type = request.GET.get('room_type') or None
        purpose = request.GET.get('purpose') or None
        results = recommend_rooms(budget=budget, guests=guests, room_type=room_type, purpose=purpose)

    context = {
        'results': results,
        'categories': RoomCategory.objects.all(),
        'purposes': Room.PURPOSE_CHOICES,
    }
    return render(request, 'rooms/recommend.html', context)


@login_required
def toggle_wishlist(request, pk):
    room = get_object_or_404(Room, pk=pk)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, room=room)
    if not created:
        wishlist_item.delete()
        added = False
    else:
        added = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'added': added})

    messages.success(request, 'Added to wishlist!' if added else 'Removed from wishlist.')
    return redirect('rooms:detail', pk=pk)


@login_required
def add_review(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        review = Review.objects.create(room=room, user=request.user, rating=rating, comment=comment)

        from adminpanel.notifications import notify_admins
        notify_admins(
            'review',
            f'New {review.get_sentiment_display().lower()} review on {room.name} by {request.user.username}',
            link='/manage/reviews/',
        )

        messages.success(request, 'Thanks for your review! Our AI has analyzed its sentiment.')
    return redirect('rooms:detail', pk=pk)
