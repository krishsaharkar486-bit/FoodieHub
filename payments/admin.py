from django.contrib import admin
from .models import Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin): list_display=('order','provider','status','amount','created_at'); list_filter=('status','provider'); search_fields=('order__number','provider_payment_id','provider_order_id'); readonly_fields=('order','provider','provider_order_id','provider_payment_id','amount','currency','status')
