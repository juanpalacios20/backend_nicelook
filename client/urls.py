from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('client', views.clientViewSet, 'client.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('client_appointment_history/<int:client_id>/', views.client_appointment_history),
]