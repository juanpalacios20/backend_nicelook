from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('review_employee', views.reviewEmployeeViewSet, 'review_employee.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('create_review/<int:client_id>/<int:employee_id>/<int:appointment_id>/', views.create_review, name='create_review'),
    path('get_reviews_client/<int:client_id>/', views.get_reviews_client, name='get_reviews_client'),
    path('update_review/<int:client_id>/<int:employee_id>/<int:appointment_id>/', views.update_review, name='update_review'),
]