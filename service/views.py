from django.shortcuts import render
from .models import Service
from .serializers import serviceSerializer
from rest_framework import viewsets

# Create your views here.

class serviceViewSet(viewsets.ModelViewSet):
    serializer_class = serviceSerializer
    queryset = Service.objects.all()
    