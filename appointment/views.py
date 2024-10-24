from django.shortcuts import render
from rest_framework import viewsets,status
from .models import Appointment
from .serializers import appointmentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date
from datetime import datetime

# Create your views here.
class appointmentViewSet(viewsets.ModelViewSet):
    serializer_class = appointmentSerializer
    queryset = Appointment.objects.all()
     
@api_view(['POST'])
def appointment_list(request):
    try:
        id = request.data.get('id')
        day = request.data.get('day')
        month = request.data.get('month')
        year = request.data.get('year')
        print(day, month, year)
        appointments_date = date(year, month, day)
        print(appointments_date)
        appointments = Appointment.objects.filter(date = appointments_date, establisment = id)
        for appointment in appointments:
            for appointment_service in appointment.services.all():
                appointment.total += appointment_service.price	
        if not appointments.exists():
            return Response({'error': "Appointments doesn't exist" },status=status.HTTP_404_NOT_FOUND)
        serializer = appointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
def reschedule(request):
    try:
        id_appointment = request.data.get('id_appointment')
        day = request.data.get('day')
        month = request.data.get('month')
        year = request.data.get('year')
        time = request.data.get('time')

        # Obtener la cita existente
        appointment = Appointment.objects.get(id=id_appointment)

        # Obtener la fecha actual de la cita
        current_date = appointment.date

        # Actualizar solo las partes específicas de la fecha (día, mes, año) si se proporcionan
        new_day = int(day) if day else current_date.day
        new_month = int(month) if month else current_date.month
        new_year = int(year) if year else current_date.year

        # Construir una nueva fecha con los valores proporcionados o los existentes
        appointment.date = datetime(year=new_year, month=new_month, day=new_day).date()

        # Si se proporciona un nuevo tiempo, actualizarlo
        if time:
            appointment.time = time

        # Guardar los cambios
        appointment.save()

        return Response(status=status.HTTP_200_OK)
    
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except ValueError:
        return Response({"error": "Invalid date or time format"}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        