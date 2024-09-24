from django.shortcuts import render
from rest_framework import viewsets
from .models import ImagenEstablecimiento
from .serializers import imagenSerializer
# Create your views here.
class imagenesViewSet(viewsets.ModelViewSet):
    serializer_class = imagenSerializer
    queryset = ImagenEstablecimiento.objects.all()
    