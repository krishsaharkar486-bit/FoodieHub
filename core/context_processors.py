def cart_summary(request):
    from cart.services import get_cart
    return {"nav_cart_count": get_cart(request)["count"]}
