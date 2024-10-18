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
    path('services_by_category/', views.filter_by_category, name='list_service_by_category'),
    path('get_photo_service/<int:establisment_id>/<int:service_id>/', views.get_photo_service, name='get_photo_service'),
    path('upload_photo_service/<int:establisment_id>/<int:service_id>/', views.upload_photo_service, name='upload_photo_service'),
    path('delete_photo_service/<int:establisment_id>/<int:service_id>/', views.delete_photo_service, name='delete_photo_service'),
]