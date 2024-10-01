from django.shortcuts import render
from rest_framework import viewsets
from .models import ReviewEmployee
from .serializers import reviewEmployeeSerializer
# Create your views here.
class reviewEmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = reviewEmployeeSerializer
    queryset = ReviewEmployee.objects.all()
    