from django.contrib import admin
from .models import Booking, Payment


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'user', 'check_in', 'check_out', 'status', 'total_amount')
    list_filter = ('status', 'check_in')
    search_fields = ('user__username', 'room__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'booking', 'method', 'amount', 'status', 'paid_at')
    list_filter = ('method', 'status')
