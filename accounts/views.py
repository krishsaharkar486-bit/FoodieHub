from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import RegisterForm, AddressForm
from .models import Address
from orders.models import Order

def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user=form.save(); login(request,user); messages.success(request,'Welcome to FoodieHub!'); return redirect('home')
    return render(request,'accounts/register.html',{'form':form})

def login_view(request):
    form=AuthenticationForm(request,data=request.POST or None)
    if request.method=='POST' and form.is_valid():
        login(request,form.get_user()); next_url=request.GET.get('next','')
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}): next_url='home'
        return redirect(next_url)
    return render(request,'accounts/login.html',{'form':form})

@require_POST
def logout_view(request):
    logout(request); messages.info(request,'You have been signed out.'); return redirect('home')

@login_required
def profile(request):
    if request.method=='POST':
        u=request.user; email=request.POST.get('email',u.email).strip().lower()
        try: validate_email(email)
        except ValidationError: email=''
        if not email or u.__class__.objects.filter(email__iexact=email).exclude(pk=u.pk).exists():
            messages.error(request,'Enter a valid, unused email address.')
        else:
            u.first_name=request.POST.get('first_name','').strip()[:150]; u.last_name=request.POST.get('last_name','').strip()[:150]; u.email=email; u.save(); messages.success(request,'Profile updated.'); return redirect('accounts:profile')
    return render(request,'accounts/profile.html')

@login_required
def addresses(request):
    form=AddressForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        obj=form.save(commit=False); obj.user=request.user
        if obj.is_default: Address.objects.filter(user=request.user).update(is_default=False)
        obj.save(); messages.success(request,'Address saved.'); return redirect('accounts:addresses')
    return render(request,'accounts/addresses.html',{'form':form,'addresses':Address.objects.filter(user=request.user)})

@login_required
@require_POST
def delete_address(request,pk):
    get_object_or_404(Address,pk=pk,user=request.user).delete(); messages.success(request,'Address removed.'); return redirect('accounts:addresses')

@login_required
def dashboard(request):
    orders=Order.objects.filter(customer=request.user).select_related('restaurant')
    return render(request,'accounts/dashboard.html',{'orders':orders[:5],'order_count':orders.count(),'address_count':request.user.addresses.count()})

@login_required
def edit_address(request,pk):
    obj=get_object_or_404(Address,pk=pk,user=request.user)
    form=AddressForm(request.POST or None,instance=obj)
    if request.method=='POST' and form.is_valid():
        address=form.save(commit=False)
        if address.is_default: Address.objects.filter(user=request.user).exclude(pk=obj.pk).update(is_default=False)
        address.save(); messages.success(request,'Address updated.'); return redirect('accounts:addresses')
    return render(request,'accounts/address_edit.html',{'form':form,'address':obj})
