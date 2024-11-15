from django.shortcuts import get_object_or_404, render
import requests
from rest_framework import viewsets,status

from client.models import Client
from establisment.models import Establisment
from service.models import Service
from .models import Appointment
from .serializers import appointmentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date
from datetime import datetime
from schedule.models import Schedule, Time
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime, timedelta
from schedule.google_calendar import GoogleCalendarService
from employee.models import Employee
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from .models import Appointment, Employee, Client

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
from rest_framework.response import Response

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
        print(day, month, year, time)

        if not id_appointment or not day or not month or not year:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener la cita existente
        appointment = Appointment.objects.get(id=id_appointment)

        new_date = date(year=int(year), month=int(month), day=int(day))
        day_date = " "
        if new_date.weekday() == 0:
            day_date = "Lun"
        elif new_date.weekday() == 1:
            day_date = "Mar"
        elif new_date.weekday() == 2:
            day_date = "Mie"    
        elif new_date.weekday() == 3:
            day_date = "Jue"
        elif new_date.weekday() == 4:
            day_date = "Vie"
        elif new_date.weekday() == 5:
            day_date = "Sab"
        elif new_date.weekday() == 6:    
            day_date = "Dom"

        if Appointment.objects.filter(date=new_date, establisment=appointment.establisment, employee=appointment.employee).exists():
            return Response({"error": "appointment date not available"}, status=status.HTTP_400_BAD_REQUEST)
        
        time_employee = Time.objects.filter(employee=appointment.employee).first()
        if time_employee:
            if day_date.lower() not in [d.lower() for d in time_employee.working_days]:
                return Response({"error": "Off-agenda employee note."}, status=status.HTTP_400_BAD_REQUEST)
        
        if appointment.estate == "Completada" or appointment.estate == "Cancelada":
            return Response({"error": "appointment canceled or completed"}, status=status.HTTP_400_BAD_REQUEST)

        appointment.date = new_date
        # Si se proporciona un nuevo tiempo, actualizarlo
        if time:
            time = datetime(year=int(year), month=int(month), day=int(day), hour=int(time.split(':')[0]), minute=int(time.split(':')[1]))
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

@api_view(['PATCH'])
def change_state(request):
    try: 
        id_appointment = request.data.get('id_appointment')
        state = request.data.get('state')
        if not id_appointment or not state:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        # Obtener la cita existente
        appointment = Appointment.objects.get(id=id_appointment)
        if state == "Completada":
            appointment.estate = "Completada"
        elif state == "Cancelada":
            appointment.estate = "Cancelada"
        else:
            return Response({"error": "Invalid state value"}, status=status.HTTP_400_BAD_REQUEST)
        # Guardar los cambios
        appointment.save()
        return Response(status=status.HTTP_200_OK)
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

def generate_time_slots(start_time, end_time, slot_duration=timedelta(minutes=60)):
    slots = []
    current_time = start_time
    while current_time + slot_duration <= end_time:
        slots.append(current_time)
        current_time += slot_duration
    return slots


def get_available_times(employee_id, date):
    # Filtra los registros de tiempo del empleado y verifica el estado
    time_entries = Time.objects.filter(employee_id=employee_id, state=True)
    available_slots = []

    for entry in time_entries:
        # Comprueba si el día solicitado está en los días laborables del empleado
        if date.strftime("%A") in entry.working_days:
            # Genera los horarios del primer turno del día
            start_time = datetime.combine(date, entry.time_start_day_one)
            end_time = datetime.combine(date, entry.time_end_day_one)
            available_slots += generate_time_slots(start_time, end_time)

            # Si el empleado trabaja en dos turnos
            if entry.double_day:
                start_time = datetime.combine(date, entry.time_start_day_two)
                end_time = datetime.combine(date, entry.time_end_day_two)
                available_slots += generate_time_slots(start_time, end_time)

    # Filtrar los horarios ocupados por citas ya existentes
    appointments = Appointment.objects.filter(employee_id=employee_id, time__date=date)
    occupied_times = [appointment.time.replace(tzinfo=None) for appointment in appointments]
    print(f"Available slots: {available_slots}")
    print(f"Occupied times: {occupied_times}")
    free_slots = []
    for slot in available_slots:
        if not any(slot == occupied_time for occupied_time in occupied_times):
            free_slots.append(slot)

    return free_slots


@api_view(['GET'])
def check_availability(request, employee_id):
    # Obtenemos la fecha desde los parámetros de la solicitud
    date_str = request.query_params.get('date')
    if not date_str:
        return Response({'error': 'Date parameter is required'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    # Llamamos a la función para obtener los horarios disponibles
    available_times = get_available_times(employee_id, date)
    available_times_str = [time.isoformat() for time in available_times]
    
    return Response({'available_times': available_times_str})

@api_view(['POST'])
def create_appointment(request):
    employee_id = request.data.get('employee_id')
    date = request.data.get('date')
    time = request.data.get('time')
    client_id = request.data.get('client_id')
    services_ids = request.data.get('services')  # Lista de IDs de servicios
    establishment_id = request.data.get('establishment_id')
    
    # Paso 1: Buscar al empleado y obtener su accestoken y refresh_token
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'error': 'Empleado no encontrado.'}, status=404)

    if not employee.accestoken:
        return Response({'error': 'El empleado no tiene configurada la sincronización con Google Calendar.'}, status=400)
    
    # Paso 2: Crear el objeto Credentials con accestoken y refresh_token
    credentials = Credentials(
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxNjI1ODQwLCJpYXQiOjE3MzE2MjU1NDAsImp0aSI6ImZhMDJjOThjNmZkNTRkNmNhMDk1YmVjYzNkMDZjNTMwIiwidXNlcl9pZCI6NiwiZW1haWwiOiJqaG9zdGluLnBhekBjb3JyZW91bml2YWxsZS5lZHUuY28iLCJmaXJzdF9uYW1lIjoiSkhPU1RJTiBDQU1JTE8iLCJsYXN0X25hbWUiOiJQQVogRlJBTkNPIiwiZ29vZ2xlX2lkIjoiMTA3OTUwODA5NTY5ODczNjc0NTQyIiwiZXN0YWJsaXNobWVudCI6MSwic3RhdGUiOnRydWUsImNvZGUiOiI5MDZDRjAifQ.2gCgCFq1g8LiO4pqlDzex2KYrDH_erTr_OENT1QnDS4",
        refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMTcxMTk0MCwiaWF0IjoxNzMxNjI1NTQwLCJqdGkiOiIzZWNmYmZiZmZiNDc0NzUyODk0ZDM1MGE0ZmNiN2E3NSIsInVzZXJfaWQiOjYsImVtYWlsIjoiamhvc3Rpbi5wYXpAY29ycmVvdW5pdmFsbGUuZWR1LmNvIiwiZmlyc3RfbmFtZSI6IkpIT1NUSU4gQ0FNSUxPIiwibGFzdF9uYW1lIjoiUEFaIEZSQU5DTyIsImdvb2dsZV9pZCI6IjEwNzk1MDgwOTU2OTg3MzY3NDU0MiIsImVzdGFibGlzaG1lbnQiOjEsInN0YXRlIjp0cnVlLCJjb2RlIjoiOTA2Q0YwIn0.h3snMK-6BRXOyVyrwH1S3vJg8bV-NBef7ENlbxKxuPg",
        client_id='YOUR_CLIENT_ID',  # Reemplaza con tu Client ID
        client_secret='YOUR_CLIENT_SECRET',  # Reemplaza con tu Client Secret
        token_uri='https://oauth2.googleapis.com/token'
    )

    # Verificar si el token ha caducado y renovarlo si es necesario
    if credentials.expired:
        try:
            credentials.refresh(Request())
            # Guardamos el nuevo accestoken si fue refrescado
            employee.accestoken = credentials.token
            employee.save()
        except Exception as e:
            return Response({'error': f'Error al refrescar el token: {str(e)}'}, status=500)
    
    # Verificar que el token no esté vacío y es válido
    if not credentials.token:
        return Response({'error': 'El token de acceso no es válido.'}, status=400)


    print(f"Access Token: {credentials.token}")
    print(f"Token Expired: {credentials.expired}")

    # Paso 3: Crear el evento en Google Calendar
    event_data = {
        'summary': 'Cita de servicio',
        'description': 'Detalles de la cita con el cliente.',
        'start': {
            'dateTime': f"{date}T{time}:00",
            'timeZone': 'America/Bogota',
        },
        'end': {
            'dateTime': f"{date}T{(datetime.strptime(time, '%H:%M') + timedelta(minutes=30)).strftime('%H:%M')}:00",
            'timeZone': 'America/Bogota',
        },
        'attendees': [
            {'email': employee.user.email}  # El correo del empleado que se usó en Google
        ],
    }

    headers = {
        'Authorization': f'Bearer {credentials.token}',
        'Content-Type': 'application/json'
    }

    # Realizar la solicitud para crear el evento
    response = requests.post(
        'https://www.googleapis.com/calendar/v3/calendars/primary/events',
        headers=headers,
        json=event_data
    )

    # Imprimir la respuesta para ver qué está pasando
    print(response.status_code, response.text)

    if response.status_code != 200:
        return Response({
            'error': 'No se pudo crear el evento en Google Calendar.',
            'details': response.json()  # Muestra los detalles del error
        }, status=500)
    
    # Paso 4: Crear la cita en la base de datos
    appointment = Appointment.objects.create(
        client=client_id,
        employee=employee,
        establisment=establishment_id,
        date=date,
        time=time,
        estate='confirmed',  # Estado de la cita
        method='efectivo',
        schedule=1  # Asumimos que el ID de la agenda es '1' por defecto
    )

    services = Service.objects.filter(id__in=services_ids)
    appointment.services.set(services)
    appointment.save()

    return Response({'message': 'Cita creada y agendada en Google Calendar exitosamente.'})
