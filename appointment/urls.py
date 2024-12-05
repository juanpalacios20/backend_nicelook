from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt

router = routers.DefaultRouter()
#router.register('appointment', views.AppointmentViewSet, 'appointment.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('appointment_list/', views.appointment_list),
    path('appointment_recshedule/', views.reschedule),
    path('appointment_change_state/', views.change_state),
    path('availability/<int:employee_id>/', views.check_availability),
    path('create_appointment/', views.create_appointment),
    path('cancel_day/', views.cancel_appointments_day),
    path('client_cancel_appointment/', views.client_cancel_appointment),
    path('client_appointments_pending/<int:client_id>/', views.get_appointments_pending),
]