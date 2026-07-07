def site_context(request):
    """Global template variables available on every page."""
    context = {
        'SITE_NAME': 'StayEase',
        'SITE_TAGLINE': 'AI-Powered Hotel Booking & Management',
    }

    if getattr(request, 'user', None) and request.user.is_authenticated and request.user.is_staff:
        from adminpanel.models import Notification
        context['admin_notifications'] = Notification.objects.all()[:8]
        context['admin_unread_count'] = Notification.objects.filter(is_read=False).count()

    return context
