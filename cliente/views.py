from django.shortcuts import render
from rest_framework import viewsets
from .models import Cliente
from .serializers import clienteSerializer
# Create your views here.
class clienteViewSet(viewsets.ModelViewSet):
    serializer_class = clienteSerializer
    queryset = Cliente.objects.all()
    
