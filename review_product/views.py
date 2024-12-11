from django.shortcuts import render
from rest_framework import viewsets
from .models import ReviewProduct
from .serializers import reviewProductSerializer
# Create your views here.
class reviewProductViewSet(viewsets.ModelViewSet):
    serializer_class = reviewProductSerializer
    queryset = ReviewProduct.objects.all()
    