from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('employee', views.employeeViewSet, 'employee.views')   

urlpatterns = [
    path('all/', include(router.urls))
]