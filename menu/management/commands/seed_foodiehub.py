from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from restaurants.models import Restaurant
from menu.models import Category, FoodItem

class Command(BaseCommand):
    help = "Create demo FoodieHub restaurants, categories and dishes."
    def handle(self, *args, **options):
        User = get_user_model()
        manager, _ = User.objects.get_or_create(username="demo_manager", defaults={"email": "manager@example.test", "first_name": "Demo", "role": User.Role.RESTAURANT_MANAGER})
        if not manager.has_usable_password(): manager.set_unusable_password(); manager.save()
        restaurant, _ = Restaurant.objects.get_or_create(slug="green-bowl-kitchen", defaults={"manager": manager, "name": "Green Bowl Kitchen", "description": "Bright, comforting bowls and local favourites.", "address": "12 Market Lane, Pune", "delivery_fee": Decimal("35.00"), "delivery_minutes": 30})
        examples = [("Mains", [("Paneer Tikka Bowl", "Smoky paneer, rice, mint yogurt", "veg", "249.00"), ("Crispy Chicken Wrap", "Spiced chicken, greens, house sauce", "non_veg", "289.00"), ("Chana Masala Rice", "Slow-simmered chickpeas with basmati", "vegan", "199.00")]), ("Sides & Sweets", [("Masala Fries", "Crisp fries with house masala", "vegan", "99.00"), ("Gulab Jamun", "Warm syrup-soaked milk dumplings", "veg", "89.00")])]
        for cat_name, items in examples:
            category, _ = Category.objects.get_or_create(restaurant=restaurant, slug=slugify(cat_name), defaults={"name": cat_name})
            for name, desc, diet, price in items:
                FoodItem.objects.get_or_create(restaurant=restaurant, name=name, defaults={"category": category, "description": desc, "diet": diet, "price": Decimal(price), "is_available": True})
        self.stdout.write(self.style.SUCCESS("Demo data ready. The demo_manager password is unusable; set one with `python manage.py changepassword demo_manager` for local practice."))
