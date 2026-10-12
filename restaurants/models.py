from django.conf import settings
from django.db import models
from django.utils.text import slugify

class Restaurant(models.Model):
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="managed_restaurants")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=240)
    phone = models.CharField(max_length=30, blank=True)
    image = models.ImageField(upload_to="restaurants/", blank=True)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=35)
    delivery_minutes = models.PositiveSmallIntegerField(default=35)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["name"]
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "restaurant"
            slug, n = base, 2
            while Restaurant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self): return self.name
