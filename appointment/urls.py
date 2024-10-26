from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('appointment', views.appointmentViewSet, 'appointment.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('appointment_list/', views.appointment_list),
    path('appointment_recshedule/', views.reschedule),
    path('appointment_change_state/', views.change_state),
]