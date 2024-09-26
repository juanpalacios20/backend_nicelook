from django.urls import path
from nicelook_api.views import crearEstablecimiento, cambiar_direccion, cambiar_nombre

urlpatterns = [
    path('crear-establecimiento/', crearEstablecimiento, name='crear-establecimiento'),
    path('cambiar-direccion/', cambiar_direccion, name='cambiar-direccion'),
    path('cambiar-nombre/', cambiar_nombre, name='cambiar-nombre'),
]