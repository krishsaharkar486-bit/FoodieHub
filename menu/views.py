from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import FoodItem, Category

def listing(request):
    availability=request.GET.get('availability','available')
    if availability not in {'available','unavailable','all'}: availability='available'
    qs = FoodItem.objects.filter(restaurant__is_open=True).select_related("restaurant", "category")
    q = request.GET.get("q", "").strip()[:80]
    if availability == 'available': qs=qs.filter(is_available=True)
    elif availability == 'unavailable': qs=qs.filter(is_available=False)
    if q: qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)
    category = request.GET.get("category", "")
    if category.isdigit(): qs = qs.filter(category_id=int(category))
    diet = request.GET.get("diet", "")
    if diet in FoodItem.Diet.values: qs = qs.filter(diet=diet)
    for param, lookup in (("min_price", "price__gte"), ("max_price", "price__lte")):
        value = request.GET.get(param, "").strip()
        if value:
            try:
                amount = Decimal(value)
                if amount < 0 or amount > Decimal("100000"): raise InvalidOperation
                qs = qs.filter(**{lookup: amount})
            except InvalidOperation: pass
    sort = request.GET.get("sort", "name")
    if sort in {"price", "-price", "name", "-name"}: qs = qs.order_by(sort)
    page = Paginator(qs.distinct(), 12).get_page(request.GET.get("page"))
    return render(request, "menu/list.html", {"page_obj": page, "categories": Category.objects.filter(restaurant__is_open=True).distinct(), "query": q})

def detail(request, pk):
    food = get_object_or_404(FoodItem.objects.select_related("restaurant", "category"), pk=pk, is_available=True, restaurant__is_open=True)
    return render(request, "menu/detail.html", {"food": food})
