from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('receptionist', views.receptionistViewSet, 'receptionist.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('sales/', views.appointments),
    path('products_sold/', views.products_sold),
    path('create_appoinment/', views.create_appoinment),
    path('create_sale/', views.create_sale),
]