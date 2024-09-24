from django.shortcuts import render
from rest_framework import viewsets
from .models import Administrador
from .serializers import administradorSerializer
# Create your views here.
class administradorViewSet(viewsets.ModelViewSet):
    serializer_class = administradorSerializer
    queryset = Administrador.objects.all()
    
