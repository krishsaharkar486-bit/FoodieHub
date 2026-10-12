from django.shortcuts import render
from django.views.generic import TemplateView
from restaurants.models import Restaurant
from menu.models import Category, FoodItem


def home(request):
    restaurants = Restaurant.objects.filter(is_open=True).prefetch_related("food_items")[:6]
    categories = Category.objects.filter(restaurant__is_open=True).distinct()[:8]
    foods = FoodItem.objects.filter(is_available=True, restaurant__is_open=True).select_related("restaurant", "category")[:8]
    return render(request, "core/home.html", {"restaurants": restaurants, "categories": categories, "foods": foods})

class AboutView(TemplateView): template_name = "core/about.html"
class ContactView(TemplateView): template_name = "core/contact.html"

def permission_denied(request, exception=None): return render(request, 'core/403.html', status=403)
def not_found(request, exception=None): return render(request, 'core/404.html', status=404)
def server_error(request): return render(request, 'core/500.html', status=500)
