from django.conf import settings
from django.db import models
from restaurants.models import Restaurant
from menu.models import FoodItem

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PREPARING = "preparing", "Preparing"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
    class PaymentMethod(models.TextChoices):
        COD = "cod", "Cash on Delivery"
        RAZORPAY = "razorpay", "Razorpay"
    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="orders")
    number = models.CharField(max_length=24, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    payment_method = models.CharField(max_length=12, choices=PaymentMethod.choices, default=PaymentMethod.COD)
    payment_status = models.CharField(max_length=12, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    customer_name = models.CharField(max_length=120)
    contact_phone = models.CharField(max_length=25)
    address_text = models.TextField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return self.number
    @property
    def can_cancel(self): return self.status in {self.Status.PENDING, self.Status.CONFIRMED} and self.payment_status != self.PaymentStatus.PAID

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_lines")
    name_snapshot = models.CharField(max_length=120)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self): return f"{self.quantity} × {self.name_snapshot}"
