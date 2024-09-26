from django.shortcuts import render
from rest_framework import viewsets
from .models import Payment
from .serializers import paymentSerializer
# Create your views here.
class paymentViewSet(viewsets.ModelViewSet):
    serializer_class = paymentSerializer
    queryset =Payment.objects.all()
    