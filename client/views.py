from django.shortcuts import render
from rest_framework import viewsets
from .models import Client
from .serializers import clientSerializer
from rest_framework.decorators import api_view
from appointment.models import Appointment
from rest_framework.response import Response
from rest_framework import status
from appointment.serializers import appointmentSerializer
# Create your views here.
class clientViewSet(viewsets.ModelViewSet):
    serializer_class = clientSerializer
    queryset = Client.objects.all()
    
    
@api_view(['GET'])
def client_appointment_history(request, client_id):
    
    try:
        client = Client.objects.get(id=client_id)
        appointments = Appointment.objects.filter(client=client).order_by('-date')
        
        if not appointments.exists():
            return Response({'message': 'No appointments found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = appointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    
    
    
      


    
    
    
    
