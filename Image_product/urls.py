from django.contrib import admin
from django.urls import path ,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('image_product', views.ImageProduct , 'image_product.views')   

urlpatterns = [
    
    path('addImage/', views.uploadImage, name='add_image_product'),
    path('getImage/', views.getImageProduct, name='get_image_product'),
    path('updateImage/', views.updateImageProduct, name='update_image_product'),
    path('deleteImage/', views.deleteImageProduct, name='delete_image_product'),
    
]

    