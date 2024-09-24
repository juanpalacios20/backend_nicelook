from django.urls import path
from nicelook_api.views import guardar_color
from nicelook_api.views import obtener_color

urlpatterns = [
    path('guardar-color/<int:establecimiento_id>/', guardar_color, name='guardar_color'),
    path('obtener-color/<int:color_id>/', obtener_color, name='obtener_color'),
]
