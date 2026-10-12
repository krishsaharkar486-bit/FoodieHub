from django.db import models
from restaurants.models import Restaurant

class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=70)
    slug = models.SlugField(max_length=90)
    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["restaurant", "slug"], name="unique_category_slug_per_restaurant")]
    def __str__(self): return f"{self.name} · {self.restaurant.name}"

class FoodItem(models.Model):
    class Diet(models.TextChoices):
        VEGETARIAN = "veg", "Vegetarian"
        NON_VEGETARIAN = "non_veg", "Non-vegetarian"
        VEGAN = "vegan", "Vegan"
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="food_items")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="items")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="food/", blank=True)
    diet = models.CharField(max_length=10, choices=Diet.choices, default=Diet.VEGETARIAN)
    is_available = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["restaurant", "is_available"]), models.Index(fields=["price"])]
    def __str__(self): return f"{self.name} ({self.restaurant.name})"
