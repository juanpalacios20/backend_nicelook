from django.shortcuts import render
from rest_framework import viewsets
from .models import Schedule
from .serializers import scheduleSerializer
# Create your views here.
class scheduleViewSet(viewsets.ModelViewSet):
    serializer_class = scheduleSerializer
    queryset = Schedule.objects.all()
    
