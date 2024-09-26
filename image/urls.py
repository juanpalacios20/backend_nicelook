from django.urls import path
from nicelook_api.views import subir_logo, obtener_logo, actualizar_logo, borrar_logo, subir_banner, obtener_banner, borrar_banner

urlpatterns = [
    #para el logo
    path('subir-logo/<int:establecimiento_id>/', subir_logo, name='subir_logo'),
    path('obtener-logo/<int:establecimiento_id>/', obtener_logo, name='obtener_logo'),
    path('actualizar-logo/<int:establecimiento_id>/', actualizar_logo, name='actualizar_logo'),
    path('borrar-logo/<int:establecimiento_id>/', borrar_logo, name='borrar_logo'),
    
    #para el banner
    path('subir-banner/<int:establecimiento_id>/', subir_banner, name='subir_banner'),
    path('obtener-banner/<int:establecimiento_id>/', obtener_banner, name='obtener_banner'),
    path('borrar-banner/<int:establecimiento_id>/', borrar_banner, name='borrar_banner'),
]