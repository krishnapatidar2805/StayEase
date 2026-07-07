from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Avg

from rooms.models import Room, RoomCategory
from reviews.models import Review, ContactMessage


def home_view(request):
    featured_rooms = Room.objects.filter(is_available=True).order_by('-rating')[:6]
    categories = RoomCategory.objects.all()[:6]
    top_reviews = Review.objects.filter(sentiment='positive').select_related('user', 'room')[:6]

    context = {
        'featured_rooms': featured_rooms,
        'categories': categories,
        'top_reviews': top_reviews,
        'total_rooms': Room.objects.count(),
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    return render(request, 'core/about.html')


def faq_view(request):
    faqs = [
        ("What time is check-in and check-out?", "Check-in is from 12:00 PM and check-out is by 11:00 AM."),
        ("Can I cancel my booking?", "Yes, free cancellation up to 24 hours before check-in from your dashboard."),
        ("What payment methods are supported?", "We support UPI and Credit/Debit cards."),
        ("Is breakfast included?", "Most rooms include complimentary breakfast — check the room's amenity list."),
        ("How do I get my invoice?", "Download a PDF invoice anytime from 'My Bookings' in your dashboard."),
        ("Do you offer family or group rooms?", "Yes — use the guest-count filter on the Rooms page to find rooms that fit your group."),
    ]
    return render(request, 'core/faq.html', {'faqs': faqs})


def contact_view(request):
    if request.method == 'POST':
        msg = ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        from adminpanel.notifications import notify_admins
        notify_admins(
            'contact',
            f'New contact message from {msg.name}: {msg.subject}',
            link='/manage/',
        )
        messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
        return redirect('core:contact')
    return render(request, 'core/contact.html')
