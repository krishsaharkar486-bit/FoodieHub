from django.urls import path
from . import views
app_name='accounts'
urlpatterns=[path('register/',views.register,name='register'),path('login/',views.login_view,name='login'),path('logout/',views.logout_view,name='logout'),path('dashboard/',views.dashboard,name='dashboard'),path('profile/',views.profile,name='profile'),path('addresses/<int:pk>/edit/',views.edit_address,name='edit_address'),path('addresses/',views.addresses,name='addresses'),path('addresses/<int:pk>/delete/',views.delete_address,name='delete_address')]
