from django.db import models
from orders.models import Order

class Payment(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Successful"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="payment")
    provider = models.CharField(max_length=20, default="razorpay")
    provider_order_id = models.CharField(max_length=100, blank=True, db_index=True)
    provider_payment_id = models.CharField(max_length=100, blank=True, unique=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"{self.order.number}: {self.get_status_display()}"
