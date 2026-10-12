from decimal import Decimal
from menu.models import FoodItem

SESSION_KEY = "foodiehub_cart"

def get_cart(request):
    raw = request.session.get(SESSION_KEY, {})
    ids = [int(k) for k, v in raw.items() if str(k).isdigit() and str(v).isdigit() and 0 < int(v) <= 30]
    items = list(FoodItem.objects.filter(pk__in=ids, is_available=True, restaurant__is_open=True).select_related("restaurant"))
    qty_map = {str(k): int(v) for k, v in raw.items() if str(k).isdigit() and str(v).isdigit() and 0 < int(v) <= 30}
    lines = [{"food": f, "quantity": qty_map[str(f.pk)], "line_total": f.price * qty_map[str(f.pk)]} for f in items]
    subtotal = sum((line["line_total"] for line in lines), Decimal("0.00"))
    restaurant = items[0].restaurant if items else None
    fee = restaurant.delivery_fee if restaurant else Decimal("0.00")
    return {"lines": lines, "subtotal": subtotal, "delivery_fee": fee, "total": subtotal + fee,
            "count": sum(line["quantity"] for line in lines), "restaurant": restaurant}

def add_item(request, food, quantity=1):
    cart = request.session.get(SESSION_KEY, {})
    if cart:
        existing = FoodItem.objects.filter(pk__in=[int(x) for x in cart if str(x).isdigit()]).first()
        if existing and existing.restaurant_id != food.restaurant_id:
            raise ValueError("Your cart contains food from another restaurant. Please empty it before adding this item.")
    current = int(cart.get(str(food.pk), 0))
    if current + quantity > 30: raise ValueError("You can order up to 30 of each item.")
    cart[str(food.pk)] = current + quantity
    request.session[SESSION_KEY] = cart
    request.session.modified = True

def update_item(request, food_id, quantity):
    cart = request.session.get(SESSION_KEY, {})
    if quantity <= 0: cart.pop(str(food_id), None)
    elif quantity > 30: raise ValueError("Maximum quantity is 30.")
    elif str(food_id) in cart: cart[str(food_id)] = quantity
    request.session[SESSION_KEY] = cart
    request.session.modified = True
