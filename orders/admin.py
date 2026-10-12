from django.contrib import admin
from .models import Order, OrderItem
class OrderItemInline(admin.TabularInline): model=OrderItem; extra=0; readonly_fields=('name_snapshot','unit_price','quantity','line_total')
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin): list_display=('number','customer','restaurant','status','payment_method','payment_status','total','created_at'); list_filter=('status','payment_method','payment_status','created_at'); search_fields=('number','customer__username'); readonly_fields=('number','subtotal','delivery_fee','total','address_text'); inlines=(OrderItemInline,)
