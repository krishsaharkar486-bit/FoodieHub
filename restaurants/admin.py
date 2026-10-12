from django.contrib import admin
from .models import Restaurant
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin): list_display=('name','manager','is_open','delivery_fee'); list_filter=('is_open',); search_fields=('name','manager__username')
