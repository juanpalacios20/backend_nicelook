from django.shortcuts import render
from rest_framework import viewsets
from .models import Establisment
from .serializers import establismentSerializer
# Create your views here.
class establismentViewSet(viewsets.ModelViewSet):
    serializer_class = establismentSerializer
    queryset = Establisment.objects.all()
    
