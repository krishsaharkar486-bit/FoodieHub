from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        RESTAURANT_MANAGER = "restaurant_manager", "Restaurant Manager"
        ADMIN = "admin", "Website Administrator"
    role = models.CharField(max_length=24, choices=Role.choices, default=Role.CUSTOMER)
    email = models.EmailField(unique=True)
    def __str__(self): return self.get_full_name() or self.username

class Address(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=40, default="Home")
    recipient_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=25)
    line1 = models.CharField(max_length=180)
    line2 = models.CharField(max_length=180, blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80, blank=True)
    postal_code = models.CharField(max_length=12)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-is_default", "-created_at"]
    def __str__(self): return f"{self.label}: {self.line1}, {self.city}"
