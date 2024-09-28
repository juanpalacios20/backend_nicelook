from django.urls import path
from .views import upload_color, get_color

urlpatterns = [
    #para el logo
    path('get-color/<int:establisment_id>/', get_color, name='get-color'),
    path('upload-logo/<int:establisment_id>/', upload_color, name='upload-color'),
]