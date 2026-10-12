import secrets
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from accounts.models import Address
from cart.services import get_cart, SESSION_KEY
from payments.models import Payment
from restaurants.models import Restaurant
from .models import Order, OrderItem
from .services import change_status

@login_required
def checkout(request):
    cart=get_cart(request)
    if not cart['lines']:
        messages.info(request,'Your cart is empty.'); return redirect('cart:view')
    addresses=Address.objects.filter(user=request.user)
    if not addresses.exists():
        messages.info(request,'Add a delivery address before checkout.'); return redirect('accounts:addresses')
    if request.method=='GET':
        nonce=secrets.token_urlsafe(18); request.session['checkout_nonce']=nonce
        return render(request,'orders/checkout.html',{'cart':cart,'addresses':addresses,'nonce':nonce,'online_enabled':bool(__import__('os').environ.get('RAZORPAY_KEY_ID') and __import__('os').environ.get('RAZORPAY_KEY_SECRET'))})
    if request.POST.get('nonce') != request.session.get('checkout_nonce'):
        messages.error(request,'This checkout was already submitted or expired. Review your cart and try again.'); return redirect('cart:view')
    address=get_object_or_404(Address,user=request.user,pk=request.POST.get('address'))
    method=request.POST.get('payment_method',Order.PaymentMethod.COD)
    if method not in Order.PaymentMethod.values: method=Order.PaymentMethod.COD
    if method==Order.PaymentMethod.RAZORPAY and not (__import__('os').environ.get('RAZORPAY_KEY_ID') and __import__('os').environ.get('RAZORPAY_KEY_SECRET')):
        messages.error(request,'Online payment is not configured. Choose Cash on Delivery.'); return redirect('orders:checkout')
    ids=[line['food'].pk for line in cart['lines']]
    try:
        with transaction.atomic():
            foods={f.pk:f for f in __import__('menu.models',fromlist=['FoodItem']).FoodItem.objects.select_for_update().filter(pk__in=ids,is_available=True,restaurant__is_open=True)}
            if len(foods)!=len(set(ids)): raise ValueError('A cart item is no longer available. Please review your cart.')
            restaurant_ids={f.restaurant_id for f in foods.values()}
            if len(restaurant_ids)!=1: raise ValueError('A cart can contain items from only one restaurant.')
            restaurant=Restaurant.objects.get(pk=next(iter(restaurant_ids)),is_open=True)
            subtotal=sum((foods[x['food'].pk].price*x['quantity'] for x in cart['lines']),Decimal('0.00'))
            fee=restaurant.delivery_fee; total=subtotal+fee
            order=Order.objects.create(customer=request.user,restaurant=restaurant,number='FH'+secrets.token_hex(5).upper(),status=Order.Status.PENDING,payment_method=method,payment_status=Order.PaymentStatus.PENDING if method==Order.PaymentMethod.RAZORPAY else Order.PaymentStatus.UNPAID,customer_name=address.recipient_name,contact_phone=address.phone,address_text=', '.join(x for x in [address.line1,address.line2,address.city,address.state,address.postal_code] if x),subtotal=subtotal,delivery_fee=fee,total=total)
            for line in cart['lines']:
                food=foods[line['food'].pk]; qty=line['quantity']
                OrderItem.objects.create(order=order,food_item=food,name_snapshot=food.name,unit_price=food.price,quantity=qty,line_total=food.price*qty)
            if method==Order.PaymentMethod.RAZORPAY: Payment.objects.create(order=order,amount=total,status=Payment.Status.CREATED)
    except (ValueError, Restaurant.DoesNotExist) as exc:
        messages.error(request,str(exc)); return redirect('cart:view')
    request.session.pop(SESSION_KEY,None); request.session.pop('checkout_nonce',None)
    if method==Order.PaymentMethod.RAZORPAY:
        try:
            from payments.gateway import create_gateway_order
            gateway_order,key_id=create_gateway_order(total,order.number)
            payment=order.payment; payment.provider_order_id=gateway_order['id']; payment.status=Payment.Status.PENDING; payment.save()
            return render(request,'orders/checkout.html',{'order':order,'gateway_order_id':gateway_order['id'],'key_id':key_id,'amount_paise':int(total*100),'online_enabled':True})
        except Exception as exc:
            order.payment_status=Order.PaymentStatus.FAILED; order.save(update_fields=['payment_status'])
            order.payment.status=Payment.Status.FAILED; order.payment.save(update_fields=['status','updated_at'])
            messages.error(request,f'Razorpay could not start payment ({exc}). Your order is recorded with payment failed; contact the restaurant or reorder using Cash on Delivery.')
    return redirect('orders:confirmation',number=order.number)

@login_required
def my_orders(request): return render(request,'orders/list.html',{'orders':Order.objects.filter(customer=request.user).select_related('restaurant')})

@login_required
def detail(request,number):
    order=get_object_or_404(Order.objects.prefetch_related('items').select_related('restaurant'),number=number,customer=request.user)
    return render(request,'orders/detail.html',{'order':order,'steps':[Order.Status.PENDING,Order.Status.CONFIRMED,Order.Status.PREPARING,Order.Status.OUT_FOR_DELIVERY,Order.Status.DELIVERED]})

@login_required
def confirmation(request,number):
    order=get_object_or_404(Order.objects.prefetch_related('items'),number=number,customer=request.user)
    return render(request,'orders/confirmation.html',{'order':order})

@login_required
@require_POST
def cancel(request,number):
    order=get_object_or_404(Order,number=number,customer=request.user)
    try: change_status(order,Order.Status.CANCELLED); messages.success(request,'Order cancelled.')
    except Exception as exc: messages.error(request,str(exc))
    return redirect('orders:detail',number=number)
