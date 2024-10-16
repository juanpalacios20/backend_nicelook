from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('category', views.categoryViewSet, 'category.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('category_list/', views.category_list),
]