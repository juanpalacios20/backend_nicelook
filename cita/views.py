from django.shortcuts import render
from rest_framework import viewsets
from .models import Cita
from .serializers import citaSerializer
# Create your views here.
class citaViewSet(viewsets.ModelViewSet):
    serializer_class = citaSerializer
    queryset = Cita.objects.all()
    
