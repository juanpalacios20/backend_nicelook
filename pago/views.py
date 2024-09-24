from django.shortcuts import render
from rest_framework import viewsets
from .models import Pago
from .serializers import pagoSerializer
# Create your views here.
class pagoViewSet(viewsets.ModelViewSet):
    serializer_class = pagoSerializer
    queryset =Pago.objects.all()
    