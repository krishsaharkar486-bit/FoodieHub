from django.shortcuts import get_object_or_404, render
from .models import Restaurant

def listing(request):
    qs = Restaurant.objects.filter(is_open=True)
    term = request.GET.get("q", "").strip()[:80]
    if term: qs = qs.filter(name__icontains=term) | qs.filter(description__icontains=term)
    return render(request, "restaurants/list.html", {"restaurants": qs.distinct(), "query": term})

def detail(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug, is_open=True)
    foods = restaurant.food_items.filter(is_available=True).select_related("category")
    return render(request, "restaurants/detail.html", {"restaurant": restaurant, "foods": foods, "categories": restaurant.categories.all()})
