from django.urls import path 
from .views import get_payment_employee

urlpatterns = [
    path('get-payment-employee/<int:establisment_id>/', get_payment_employee, name='get-payment-employee'),
]