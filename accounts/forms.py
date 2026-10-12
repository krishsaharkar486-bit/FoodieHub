from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Address

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists(): raise forms.ValidationError("An account with this email already exists.")
        return email

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ("label", "recipient_name", "phone", "line1", "line2", "city", "state", "postal_code", "is_default")
        widgets = {"label": forms.TextInput(attrs={"placeholder": "Home, Work…"})}
