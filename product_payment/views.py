from django.shortcuts import render
from rest_framework import viewsets
from .models import Product_payment
from .serializers import productPaymentSerializer
# Create your views here.
class productPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = productPaymentSerializer
    queryset =Product_payment.objects.all()
    