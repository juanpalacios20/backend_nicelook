from django.shortcuts import render
from rest_framework import viewsets
from .models import Producto
from .serializers import productoSerializer
# Create your views here.
class productoViewSet(viewsets.ModelViewSet):
    serializer_class = productoSerializer
    queryset =Producto.objects.all()
    