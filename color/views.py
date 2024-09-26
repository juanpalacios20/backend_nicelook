from django.shortcuts import render
from rest_framework import viewsets
from .models import Color
from .serializer import colorSerializer
# Create your views here.
class colorViewSet(viewsets.ModelViewSet):
    serializer_class = colorSerializer
    queryset = Color.objects.all()
