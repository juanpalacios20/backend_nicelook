from django.shortcuts import render
from rest_framework import viewsets,status
from .models import Appointment
from .serializers import appointmentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
class appointmentViewSet(viewsets.ModelViewSet):
    serializer_class = appointmentSerializer
    queryset = Appointment.objects.all()
    
@api_view(['GET'])
def appointment_list(request):
    try:
        print("I am here")
        appointments = Appointment.objects.all()
        print(appointments)
        serializer = appointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)