from django.urls import path
from .views import createEstablisment, update_establisment, get_establisment, get_filter_payments_service, get_filter_payments_product


urlpatterns = [
    path('create-establisment/', createEstablisment, name='create-establisment'),
    path('update-establisment/<int:establisment_id>/', update_establisment, name='update-establisment'),
    path('get-establisment/<int:establisment_id>/', get_establisment, name='get-establisment'),
    path('get-filter-payments-service/<int:establisment_id>/', get_filter_payments_service, name='get-filter-payments-service'),
    path('get-filter-payments-product/<int:establisment_id>/', get_filter_payments_product, name='get-filter-payments-product'),
]