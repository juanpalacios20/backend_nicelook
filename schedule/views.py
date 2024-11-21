from django.shortcuts import render
from rest_framework import viewsets
from .models import Schedule
from .serializers import scheduleSerializer
from rest_framework.decorators import api_view
# Create your views here.
class scheduleViewSet(viewsets.ModelViewSet):
    serializer_class = scheduleSerializer
    queryset = Schedule.objects.all()
    
#@api_view(["GET"])