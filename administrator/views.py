from django.shortcuts import render
from rest_framework import viewsets
from .models import Administrator
from .serializers import administratorSerializer
# Create your views here.
class administratorViewSet(viewsets.ModelViewSet):
    serializer_class = administratorSerializer
    queryset = Administrator.objects.all()
    
