from django.shortcuts import render
from rest_framework import viewsets
from .models import Colores
from .serializer import coloresSerializer
# Create your views here.
class coloresViewSet(viewsets.ModelViewSet):
    serializer_class = coloresSerializer
    queryset = Colores.objects.all()
