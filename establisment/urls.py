from django.urls import path
from .views import createEstablisment, update_establisment, get_establisment

urlpatterns = [
    path('create-establisment/', createEstablisment, name='create-establisment'),
    path('update-establisment/<int:establisment_id>/', update_establisment, name='update-establisment'),
    path('get-establisment/<int:establisment_id>/', get_establisment, name='get-establisment'),
]