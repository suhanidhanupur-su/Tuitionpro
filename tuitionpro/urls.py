"""
URL configuration for tuitionpro project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Django built-in auth views:
    # /accounts/login/   → login page
    # /accounts/logout/  → logout (POST)
    # /accounts/password_change/ etc.
    path('accounts/', include('django.contrib.auth.urls')),

    # core app — dashboard served at "/"
    path('', include('core.urls')),
]
