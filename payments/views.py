from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from orders.models import Order
from .models import Payment
from .gateway import verify_signature

@login_required
@require_POST
def verify(request):
    number=request.POST.get('order_number','')
    order=get_object_or_404(Order,number=number,customer=request.user)
    try:
        payment=order.payment
        if payment.status==Payment.Status.SUCCESS: return redirect('payments:status',number=order.number)
        if request.POST.get('razorpay_order_id') != payment.provider_order_id: raise ValueError('Payment order mismatch.')
        verify_signature(payment.provider_order_id,request.POST.get('razorpay_payment_id',''),request.POST.get('razorpay_signature',''))
        payment.provider_payment_id=request.POST.get('razorpay_payment_id',''); payment.status=Payment.Status.SUCCESS; payment.save()
        order.payment_status=Order.PaymentStatus.PAID; order.save(update_fields=['payment_status'])
        messages.success(request,'Payment verified successfully.')
    except Exception as exc:
        if hasattr(order,'payment'):
            payment=order.payment; payment.status=Payment.Status.FAILED; payment.save(update_fields=['status','updated_at'])
            order.payment_status=Order.PaymentStatus.FAILED; order.save(update_fields=['payment_status'])
        messages.error(request,f'Payment verification failed: {exc}')
    return redirect('payments:status',number=number)

@login_required
def status(request,number):
    order=get_object_or_404(Order,number=number,customer=request.user)
    payment=Payment.objects.filter(order=order).first()
    return render(request,'payments/status.html',{'order':order,'payment':payment})
