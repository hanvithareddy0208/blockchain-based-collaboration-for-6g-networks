"""
6G Blockchain System URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from core.views import CustomLoginView, CustomLogoutView, register

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
    path('accounts/register/', register, name='register'),
    path('register/', register, name='register'),
    
    # Other authentication password views
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Redirect root to login if not authenticated, else to dashboard
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    
    # Core application URLs
    path('', include('core.urls')),
    
    # API endpoints
    path('api/', include('core.api_urls')),
]

# Custom admin site headers
admin.site.site_header = '6G Blockchain System Administration'
admin.site.site_title = '6G Blockchain Admin Portal'
admin.site.index_title = 'System Management'

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)