from django.shortcuts import render
from rest_framework import viewsets
from .models import Category
from .serializers import categorySerializer
# Create your views here.
class categoryViewSet(viewsets.ModelViewSet):
    serializer_class = categorySerializer
    queryset = Category.objects.all()
    
