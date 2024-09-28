from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('employee', views.employeeViewSet, 'employee.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('create_employee/', views.create_employee, name='create_employee'),
    path('get_employees/', views.get_employees, name='get_employees'),
    path('delete_employee/', views.delete_employee, name='delete_employee'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('search_employees/', views.search_employees, name='search_employees'),
    path('update_employee/', views.update_employee, name='update_employee'),
]