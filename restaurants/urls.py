from django.urls import path
from . import views
app_name='restaurants'
urlpatterns=[path('',views.listing,name='list'),path('<slug:slug>/',views.detail,name='detail')]
