

from django.db import router
from django.urls import include, path

from product_payment import views


urlpatterns = [
    path('create_product_payment/<establisment_id>/<client_id>/', views.create_product_payment, name='create_product_payment'),
    path('details/<payment_id>/', views.details, name='details'),
    path('cancel_payment/<payment_id>/', views.cancel_payment, name='cancel_payment'),
    path('send_email/', views.send_email_details, name='send_email_details'),
]