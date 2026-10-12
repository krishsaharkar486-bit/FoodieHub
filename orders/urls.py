from django.urls import path
from . import views
app_name='orders'
urlpatterns=[path('checkout/',views.checkout,name='checkout'),path('confirmation/<str:number>/',views.confirmation,name='confirmation'),path('mine/',views.my_orders,name='mine'),path('<str:number>/',views.detail,name='detail'),path('<str:number>/cancel/',views.cancel,name='cancel')]
