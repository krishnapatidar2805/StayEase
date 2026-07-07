from django.contrib import admin
from .models import RoomCategory, Amenity, Room, RoomImage, Wishlist


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_per_night', 'capacity', 'is_available', 'rating')
    list_filter = ('category', 'is_available', 'best_for')
    search_fields = ('name', 'description')
    inlines = [RoomImageInline]
    filter_horizontal = ('amenities',)


admin.site.register(RoomCategory)
admin.site.register(Amenity)
admin.site.register(Wishlist)
