from django.shortcuts import render
from .models import Servicio
from .serializers import servicioSerializer
from rest_framework import viewsets

# Create your views here.

class servicioViewSet(viewsets.ModelViewSet):
    serializer_class = servicioSerializer
    queryset = Servicio.objects.all()
    