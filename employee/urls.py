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
]