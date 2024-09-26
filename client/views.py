from django.shortcuts import render
from rest_framework import viewsets
from .models import Client
from .serializers import clientSerializer
# Create your views here.
class clientViewSet(viewsets.ModelViewSet):
    serializer_class = clientSerializer
    queryset = Client.objects.all()
    
