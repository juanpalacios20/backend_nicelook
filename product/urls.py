from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('product', views.productoViewSet , 'product.views')   

urlpatterns = [
    path('all/', include(router.urls)),
    path('add/', views.addProduct, name='add_product'),
    path('getAll/', views.getProducts, name='get_products'),
    path('update/', views.updateProduct, name='update_product'),
    path('delete/', views.deleteProduct, name='delete_product'),
    path('alert/<int:id_establisment>/', views.alert, name='alert_product'),
]