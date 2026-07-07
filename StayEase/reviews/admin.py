from django.contrib import admin
from .models import Review, ContactMessage


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'rating', 'sentiment', 'sentiment_score', 'created_at')
    list_filter = ('sentiment', 'rating')
    search_fields = ('comment', 'user__username')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read',)
