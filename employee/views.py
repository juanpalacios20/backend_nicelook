from django.shortcuts import render
from rest_framework import viewsets
from .models import Employee
from .serializers import employeeSerializer
# Create your views here.
class employeeViewSet(viewsets.ModelViewSet):
    serializer_class = employeeSerializer
    queryset = Employee.objects.all()
    
