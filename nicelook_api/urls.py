"""
URL configuration for nicelook_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from .social_auth_views import GoogleLogin
import service.urls
from . import views
import service

urlpatterns = [
    path('admin/', admin.site.urls),
    path('image/', include('image.urls')),
    path('establisment/', include('establisment.urls')),
    path('api/', include('appointment.urls')),
    path('employee/', include('employee.urls')),
    path('category/', include('category.urls')),
    path('Product/', include('product.urls')),#endpoints de productos
    path('Product/', include('Image_product.urls')),#endpoints de imagenes
    path('api/', include(service.urls)),
    path('auth/', include('dj_rest_auth.urls')),  # Endpoints de autenticación
    path('auth/google/', GoogleLogin.as_view(), name='google_login'), # Para el registro
    path('accounts/', include('allauth.urls')),  # Para las rutas de allauth
    path('employee_services/', include('employee_services.urls')), 
    path('administrator/', include('administrator.urls')),#endpoints de administrador
    path('receptionist/', include('receptionist.urls')), #endpoints de recepcionista
]
