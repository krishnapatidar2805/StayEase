from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.room_list_view, name='list'),
    path('recommend/', views.recommend_view, name='recommend'),
    path('<int:pk>/', views.room_detail_view, name='detail'),
    path('<int:pk>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('<int:pk>/review/', views.add_review, name='add_review'),
]
