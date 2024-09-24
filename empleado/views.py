from django.shortcuts import render
from rest_framework import viewsets
from .models import Cliente
from .serializers import empleadoSerializer
# Create your views here.
class empleadoViewSet(viewsets.ModelViewSet):
    serializer_class = empleadoSerializer
    queryset = Cliente.objects.all()
    
