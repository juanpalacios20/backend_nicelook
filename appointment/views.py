from django.shortcuts import render
from rest_framework import viewsets
from .models import Appointment
from .serializers import appointmentSerializer
# Create your views here.
class appointmentViewSet(viewsets.ModelViewSet):
    serializer_class = appointmentSerializer
    queryset = Appointment.objects.all()
    
