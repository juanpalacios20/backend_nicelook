from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('employee', views.employeeViewSet, 'employee.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('create_employee/<int:establisment_id>/', views.create_employee, name='create_employee'),
    path('get_employees/', views.get_employees, name='get_employees'),
    path('delete_employee/', views.delete_employee, name='delete_employee'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('search_employees/', views.search_employees, name='search_employees'),
    path('update_employee/', views.update_employee, name='update_employee'),
    path('upload_employee_photo/<int:establisment_id>/<int:employee_id>/', views.upload_employee_photo, name='upload_employee_photo'),
    path('get_photo/<int:establisment_id>/<int:employee_id>/', views.get_photo, name='get_employee_photo'),
    path('delete_photo/<int:establisment_id>/<int:employee_id>/', views.delete_photo, name='delete_employee_photo'),
    path('addservice/<int:employee_id>/', views.employeeAddService), 
    path('history_appointments/<int:employee_id>/', views.history_appointments, name='get_history_appointments'),
    path('schedule_employee/<int:employee_id>/', views.schedule_employee, name='schedule_employee'),
    path('create_time/<int:employee_id>/', views.create_time, name='create_time'),
    path('get_time/<int:employee_id>/', views.get_time, name='get_times'),
    path('update_time/<int:time_id>/', views.update_time, name='update_time'),
    path('delete_time/<int:time_id>/', views.delete_time, name='delete_time'),
]