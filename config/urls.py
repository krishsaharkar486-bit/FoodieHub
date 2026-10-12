from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
urlpatterns = [
 path('admin/', admin.site.urls), path('', core_views.home, name='home'),
 path('about/', core_views.AboutView.as_view(), name='about'), path('contact/', core_views.ContactView.as_view(), name='contact'),
 path('accounts/', include('accounts.urls')), path('restaurants/', include('restaurants.urls')),
 path('menu/', include('menu.urls')), path('cart/', include('cart.urls')), path('orders/', include('orders.urls')),
 path('payments/', include('payments.urls')), path('manager/', include('dashboard.urls')),
]
if settings.DEBUG: urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler403='core.views.permission_denied'; handler404='core.views.not_found'; handler500='core.views.server_error'
