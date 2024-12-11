from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('administrator', views.administratorViewSet, basename='administrator')

urlpatterns = [
    path('', include(router.urls)),  # Esto incluirá todas las rutas generadas por el router
    path('register/', views.register, name='register_admin'),
    path('login/', views.loginAdmin, name='login_admin'),
]
