from datetime import timedelta, date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Sum, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from accounts.models import User
from menu.forms import FoodItemForm, CategoryForm
from menu.models import FoodItem
from orders.models import Order
from orders.services import change_status
from restaurants.models import Restaurant
from restaurants.forms import RestaurantProfileForm

def manager_restaurant(user):
    if not user.is_authenticated or user.role != User.Role.RESTAURANT_MANAGER: raise PermissionDenied
    return get_object_or_404(Restaurant,manager=user)

@login_required
def index(request):
    restaurant=manager_restaurant(request.user); qs=Order.objects.filter(restaurant=restaurant)
    term=request.GET.get('q','').strip()[:80]; status=request.GET.get('status','')
    display_qs=qs
    if term: display_qs=display_qs.filter(Q(number__icontains=term)|Q(customer_name__icontains=term))
    if status in Order.Status.values: display_qs=display_qs.filter(status=status)
    after=request.GET.get('after',''); before=request.GET.get('before','')
    try:
        if after: display_qs=display_qs.filter(created_at__date__gte=date.fromisoformat(after))
    except ValueError: after=''
    try:
        if before: display_qs=display_qs.filter(created_at__date__lte=date.fromisoformat(before))
    except ValueError: before=''
    today=timezone.localdate(); start=today.replace(day=1)
    collected=Q(payment_status=Order.PaymentStatus.PAID) | Q(payment_method=Order.PaymentMethod.COD,status=Order.Status.DELIVERED)
    today_sales=qs.filter(created_at__date=today).filter(collected).aggregate(v=Sum('total'))['v'] or Decimal('0.00')
    month_sales=qs.filter(created_at__date__gte=start).filter(collected).aggregate(v=Sum('total'))['v'] or Decimal('0.00')
    popular=restaurant.food_items.annotate(quantity=Sum('order_lines__quantity')).order_by('-quantity')[:5]
    recent=display_qs.select_related('customer').prefetch_related('items')[:10]
    days=[today-timedelta(days=i) for i in reversed(range(7))]
    chart=[float(qs.filter(created_at__date=d,status=Order.Status.DELIVERED).aggregate(v=Sum('total'))['v'] or 0) for d in days]
    return render(request,'dashboard/index.html',{'restaurant':restaurant,'orders':qs,'recent':recent,'today_sales':today_sales,'month_sales':month_sales,'pending':qs.filter(status=Order.Status.PENDING).count(),'completed':qs.filter(status=Order.Status.DELIVERED).count(),'popular':popular,'chart_labels':[d.strftime('%a') for d in days],'chart_values':chart,'query':term,'status_filter':status,'status_choices':Order.Status.choices,'after':after,'before':before})

@login_required
def order_detail(request,number):
    restaurant=manager_restaurant(request.user); order=get_object_or_404(Order.objects.prefetch_related('items'),restaurant=restaurant,number=number)
    return render(request,'dashboard/order_detail.html',{'order':order})

@login_required
@require_POST
def update_status(request,number):
    restaurant=manager_restaurant(request.user); order=get_object_or_404(Order,restaurant=restaurant,number=number)
    try:
        change_status(order,request.POST.get('status'))
        if order.status==Order.Status.DELIVERED and order.payment_method==Order.PaymentMethod.COD:
            order.payment_status=Order.PaymentStatus.PAID; order.save(update_fields=['payment_status'])
        messages.success(request,'Order status updated.')
    except (ValidationError,ValueError) as exc: messages.error(request,str(exc))
    return redirect('dashboard:order_detail',number=number)

@login_required
def menu_manage(request):
    restaurant=manager_restaurant(request.user)
    return render(request,'dashboard/menu.html',{'restaurant':restaurant,'items':restaurant.food_items.select_related('category')})

@login_required
def food_add(request):
    restaurant=manager_restaurant(request.user); form=FoodItemForm(request.POST or None,request.FILES or None)
    form.fields['category'].queryset=restaurant.categories.all()
    if request.method=='POST' and form.is_valid():
        food=form.save(commit=False); food.restaurant=restaurant; food.save(); messages.success(request,'Menu item created.'); return redirect('dashboard:menu')
    return render(request,'dashboard/food_form.html',{'form':form,'title':'Add a menu item'})

@login_required
def food_edit(request,pk):
    restaurant=manager_restaurant(request.user); food=get_object_or_404(FoodItem,pk=pk,restaurant=restaurant)
    form=FoodItemForm(request.POST or None,request.FILES or None,instance=food); form.fields['category'].queryset=restaurant.categories.all()
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Menu item updated.'); return redirect('dashboard:menu')
    return render(request,'dashboard/food_form.html',{'form':form,'title':'Edit menu item'})

@login_required
@require_POST
def food_availability(request,pk):
    restaurant=manager_restaurant(request.user); food=get_object_or_404(FoodItem,pk=pk,restaurant=restaurant); food.is_available=not food.is_available; food.save(update_fields=['is_available','updated_at']); return redirect('dashboard:menu')

@login_required
def categories(request):
    restaurant=manager_restaurant(request.user); form=CategoryForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        if restaurant.categories.filter(slug=slugify(form.cleaned_data['name'])).exists(): form.add_error('name','This category already exists for your restaurant.')
        else: form.save(restaurant=restaurant); messages.success(request,'Category added.'); return redirect('dashboard:categories')
    return render(request,'dashboard/categories.html',{'form':form,'categories':restaurant.categories.all()})

@login_required
def restaurant_profile(request):
    restaurant=manager_restaurant(request.user); form=RestaurantProfileForm(request.POST or None,request.FILES or None,instance=restaurant)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Restaurant profile updated.'); return redirect('dashboard:index')
    return render(request,'dashboard/restaurant_form.html',{'form':form})
