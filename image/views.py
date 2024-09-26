from django.shortcuts import render
from rest_framework import viewsets
from .models import Image
from .serializers import imageSerializer
# Create your views here.
class imagenesViewSet(viewsets.ModelViewSet):
    serializer_class = imageSerializer
    queryset = Image.objects.all()
    