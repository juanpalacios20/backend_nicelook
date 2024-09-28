from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('services', views.serviceViewSet, 'services.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('create_service/', views.create_service, name='create_service'),
    path('update_service/', views.update_service, name='update_service'),
    path('delete_service/', views.delete_service, name='delete_service'),
    path('list_service/', views.list_service, name='list_service'),
]