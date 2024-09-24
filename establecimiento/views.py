from django.shortcuts import render
from rest_framework import viewsets
from .models import Establecimiento
from .serializers import establecimientoSerializer
# Create your views here.
class establecimientoViewSet(viewsets.ModelViewSet):
    serializer_class = establecimientoSerializer
    queryset = Establecimiento.objects.all()
    
