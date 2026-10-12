from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from menu.models import FoodItem
from .services import get_cart, add_item, update_item, SESSION_KEY

def view_cart(request): return render(request,'cart/cart.html',{'cart':get_cart(request)})

@require_POST
def add(request,pk):
    food=get_object_or_404(FoodItem,pk=pk,is_available=True,restaurant__is_open=True)
    try: add_item(request,food,1); messages.success(request,f'{food.name} added to your cart.')
    except ValueError as exc: messages.error(request,str(exc))
    next_url=request.POST.get('next','')
    if not url_has_allowed_host_and_scheme(next_url,allowed_hosts={request.get_host()}): next_url='cart:view'
    return redirect(next_url)

@require_POST
def update(request,pk):
    try: qty=int(request.POST.get('quantity','1'))
    except ValueError: qty=-1
    try: update_item(request,pk,qty)
    except ValueError as exc: messages.error(request,str(exc))
    return redirect('cart:view')

@require_POST
def clear(request):
    request.session[SESSION_KEY]={}; request.session.modified=True; return redirect('cart:view')
