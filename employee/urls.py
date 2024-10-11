from django.urls import path 
from .views import get_payment_employee, get_services_most_sold, get_products_most_sold

urlpatterns = [
    path('get-payment-employee/<int:establisment_id>/', get_payment_employee, name='get-payment-employee'),
    path('get-services-most-sold/<int:establisment_id>/', get_services_most_sold, name='get-services-most-sold'),
    path('get-products-most-sold/<int:establisment_id>/', get_products_most_sold, name='get-products-most-sold'),
]