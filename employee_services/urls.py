from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('employee_services', views.employeeServicesViewSet, 'employee_services.views')   

urlpatterns = [ 
    path('all/', include(router.urls)),
    path('employeeServicesList/<int:employee_id>/', views.employeeServicesList, name='employee-services-list'),
    path('employeeServiceDelete/<int:employee_id>/<int:service_id>/', views.employeeServiceDelete, name='employee-service-delete'),
]