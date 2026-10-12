from django.urls import path
from . import views
app_name='cart'
urlpatterns=[path('',views.view_cart,name='view'),path('add/<int:pk>/',views.add,name='add'),path('update/<int:pk>/',views.update,name='update'),path('clear/',views.clear,name='clear')]
