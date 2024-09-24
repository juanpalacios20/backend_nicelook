from django.shortcuts import render
from rest_framework import viewsets
from .models import Recepcionista
from .serializers import recepcionistaSerializer
# Create your views here.
class recepcionistaViewSet(viewsets.ModelViewSet):
    serializer_class = recepcionistaSerializer
    queryset = Recepcionista.objects.all()
    