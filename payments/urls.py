from django.urls import path
from . import views
app_name='payments'
urlpatterns=[path('verify/',views.verify,name='verify'),path('status/<str:number>/',views.status,name='status')]
