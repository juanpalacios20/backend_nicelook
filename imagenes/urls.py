from django.urls import path
from nicelook_api.views import subir_imagen
from nicelook_api.views import obtener_imagen

urlpatterns = [
    path('subir-imagen/<int:establecimiento_id>/', subir_imagen, name='subir_imagen'),
    path('obtener-imagen/<int:imagen_id>/', obtener_imagen, name='obtener_imagen'),
]
