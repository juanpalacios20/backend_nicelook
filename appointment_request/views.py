from django.shortcuts import render
from rest_framework import viewsets
from .models import Appointment_Request
from .serializers import AppointmentRequestSerializer

# Create your views here.
class appointment_requestViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentRequestSerializer
    queryset = Appointment_Request.objects.all()