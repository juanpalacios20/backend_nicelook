from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('client', views.clientViewSet, 'client.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('client_appointment_history/<int:client_id>/', views.client_appointment_history),
    path('get_client/<int:client_id>/', views.get_client),
    path('update_client/<int:client_id>/', views.update_client),
    path('login/', views.ClientLoginView.as_view()),
]