from django.shortcuts import render
from rest_framework import viewsets
from .models import ProductPaymentDetail
from .serializers import ProductPaymentDetailSerializer
# Create your views here.
class ProductPaymentDetailViewSet(viewsets.ModelViewSet):
    queryset = ProductPaymentDetail.objects.all()
    serializer_class = ProductPaymentDetailSerializer
    