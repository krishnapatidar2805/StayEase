from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('room/<int:pk>/book/', views.book_room_view, name='book_room'),
    path('payment/<uuid:booking_id>/', views.payment_view, name='payment'),
    path('confirmation/<uuid:booking_id>/', views.confirmation_view, name='confirmation'),
    path('history/', views.booking_history_view, name='history'),
    path('cancel/<uuid:booking_id>/', views.cancel_booking_view, name='cancel'),
    path('invoice/<uuid:booking_id>/', views.download_invoice_view, name='invoice'),
]
