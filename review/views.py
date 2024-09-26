from django.shortcuts import render
from rest_framework import viewsets
from .models import Review
from .serializers import reviewSerializer
# Create your views here.
class reviewViewSet(viewsets.ModelViewSet):
    serializer_class = reviewSerializer
    queryset = Review.objects.all()
    