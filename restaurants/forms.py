from django import forms
from .models import Restaurant
class RestaurantProfileForm(forms.ModelForm):
    class Meta:
        model=Restaurant
        fields=('name','description','address','phone','image','delivery_fee','delivery_minutes','is_open')
