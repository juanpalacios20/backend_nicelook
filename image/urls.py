from django.urls import path
from .views import upload_logo, get_logo, update_logo, delete_logo, upload_banner, get_banner, delete_banner, update_banner

urlpatterns = [
    #para el logo
    path('upload-logo/<int:establisment_id>/', upload_logo, name='upload_logo'),
    path('get-logo/<int:establisment_id>/', get_logo, name='get_logo'),
    path('update-logo/<int:establisment_id>/', update_logo, name='update_logo'),
    path('delete-logo/<int:establisment_id>/', delete_logo, name='delete_logo'),
    
    #para el banner
    path('upload-banner/<int:establisment_id>/', upload_banner, name='upload_banner'),
    path('get-banner/<int:establisment_id>/', get_banner, name='get_banner'),
    path('update-banner/<int:establisment_id>/', update_banner, name='update_banner'),
    path('delete-banner/<int:establisment_id>/', delete_banner, name='delete_banner'),
]