

from django.db import router
from django.urls import include, path

from product_payment import views


urlpatterns = [
    path('create_product_payment/<establisment_id>/<client_id>/', views.create_product_payment, name='create_product_payment'),
    path('details/<payment_id>/', views.details, name='details'),
    path('cancel_payment/<payment_id>/', views.cancel_payment, name='cancel_payment'),
    path('send_email/', views.send_email_details, name='send_email_details'),
    path('agregate_product/<payment_id>/', views.agregate_product, name='agregate_product'),
    path('complete_payment/<payment_id>/', views.complete_payment, name='complete_payment'),
    path('delete_product_of_payment/<int:payment_id>/', views.delete_product_of_payment, name='delete_product_of_payment'),
    path('filter_products/', views.filter_products, name='filter_products'),
    path('list_products/<int:establisment_id>/', views.list_products, name='list_products'),
]