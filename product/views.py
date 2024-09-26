from django.shortcuts import render
from rest_framework import viewsets
from .models import Product
from .serializers import productSerializer
# Create your views here.
class productoViewSet(viewsets.ModelViewSet):
    serializer_class = productSerializer
    queryset =Product.objects.all()
    