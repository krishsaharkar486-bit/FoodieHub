from django.urls import path
from . import views
app_name='dashboard'
urlpatterns=[path('restaurant/',views.restaurant_profile,name='restaurant_profile'),path('',views.index,name='index'),path('orders/<str:number>/',views.order_detail,name='order_detail'),path('orders/<str:number>/status/',views.update_status,name='update_status'),path('menu/',views.menu_manage,name='menu'),path('menu/add/',views.food_add,name='food_add'),path('menu/<int:pk>/edit/',views.food_edit,name='food_edit'),path('menu/<int:pk>/availability/',views.food_availability,name='food_availability'),path('categories/',views.categories,name='categories')]
