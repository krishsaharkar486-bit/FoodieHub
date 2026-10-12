from django.contrib import admin
from .models import Category, FoodItem
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): list_display=('name','restaurant'); list_filter=('restaurant',)
@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin): list_display=('name','restaurant','category','price','diet','is_available'); list_filter=('restaurant','diet','is_available'); search_fields=('name','description')
