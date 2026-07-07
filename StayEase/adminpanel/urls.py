from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),

    path('rooms/', views.room_manage_view, name='room_manage'),
    path('rooms/add/', views.room_add_view, name='room_add'),
    path('rooms/<int:pk>/edit/', views.room_edit_view, name='room_edit'),
    path('rooms/<int:pk>/delete/', views.room_delete_view, name='room_delete'),

    path('bookings/', views.booking_manage_view, name='booking_manage'),
    path('bookings/<int:pk>/status/<str:new_status>/', views.booking_update_status, name='booking_update_status'),

    path('users/', views.user_manage_view, name='user_manage'),
    path('users/<int:pk>/delete/', views.user_delete_view, name='user_delete'),
    path('users/<int:pk>/toggle/', views.user_toggle_active, name='user_toggle_active'),

    path('reviews/', views.review_manage_view, name='review_manage'),
    path('reviews/<int:pk>/delete/', views.review_delete_view, name='review_delete'),

    path('reports/', views.reports_view, name='reports'),
    path('reports/export/bookings.xlsx', views.export_bookings_excel, name='export_bookings_excel'),
    path('reports/export/revenue.pdf', views.export_revenue_pdf, name='export_revenue_pdf'),

    path('notifications/<int:pk>/', views.notification_click, name='notification_click'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
]
