from django import forms
from .models import FoodItem, Category

class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ("category", "name", "description", "ingredients", "price", "image", "diet", "is_available")
        widgets = {"description": forms.Textarea(attrs={"rows": 3}), "ingredients": forms.Textarea(attrs={"rows": 2})}

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)
    def save(self, commit=True, restaurant=None):
        obj = super().save(commit=False)
        if restaurant is not None: obj.restaurant = restaurant
        from django.utils.text import slugify
        obj.slug = slugify(obj.name)
        if commit: obj.save()
        return obj
