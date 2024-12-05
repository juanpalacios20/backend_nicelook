from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('review', views.reviewViewSet, 'review.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('create_review/<int:client_id>/<int:establisment_id>/', views.create_review),
    path('get_reviews/<int:establisment_id>/', views.get_reviews)
]