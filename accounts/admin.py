from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address
@admin.register(User)
class FoodieHubUserAdmin(UserAdmin):
    fieldsets=UserAdmin.fieldsets+(('FoodieHub role',{'fields':('role',)}),)
    add_fieldsets=UserAdmin.add_fieldsets+(('FoodieHub role',{'fields':('role',)}),)
    list_display=('username','email','first_name','last_name','role','is_staff')
    list_filter=UserAdmin.list_filter+('role',)
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin): list_display=('recipient_name','user','city','is_default'); search_fields=('recipient_name','user__username','city')
