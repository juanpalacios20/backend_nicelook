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
    
@api_view(['GET'])
def get_client(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
        serializer = clientSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['PUT'])
def update_client(request, client_id):
    try:
        client = Client.objects.get(id=client_id)  # Obtiene el cliente a actualizar
        data = request.data
        
        user = client.user
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.save()  

        client.phone = data.get('phone', client.phone)
        client.save()  

        # Serializa y responde
        serializer = clientSerializer(client)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
    
    
      


    
    
    
    
