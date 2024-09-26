from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('administrator', views.administratorViewSet, 'administrator.views')   

urlpatterns = [
    path('all/', include(router.urls)),
]