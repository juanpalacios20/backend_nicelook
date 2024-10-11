from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('establisment', views.establismentViewSet, 'establisment')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('servicesByEstablisment/<int:establisment_id>/', views.servicesByEstablisment),
]