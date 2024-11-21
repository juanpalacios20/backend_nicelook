from django.shortcuts import get_object_or_404, render
import requests
from django.shortcuts import get_object_or_404, render
import requests
from rest_framework import viewsets,status

from client.models import Client
from establisment.models import Establisment
from service.models import Service

from client.models import Client
from establisment.models import Establisment
from service.models import Service
from .models import Appointment
from .serializers import appointmentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date
from datetime import datetime
from schedule.models import Time
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
# from datetime import datetime, timedelta
# from schedule.google_calendar import GoogleCalendarService
from employee.models import Employee
from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
from .models import Appointment, Employee, Client

# import requests
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta

# import requests
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
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

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Employee, Appointment, Service  # Asegúrate de tener estos modelos
from decouple import config

@api_view(['POST'])
@csrf_exempt
def create_appointment(request):
    print("Entrando")
    #Obtenemos los datos de la solicitud
    employee_id = request.data.get('employee_id')

    year = request.data.get('year')
    month = request.data.get('month')
    day = request.data.get('day')
    
    time = request.data.get('time')
    
    services = request.data.get('services')
    
    client_id = request.data.get('cliente_id')
    
    #Construimos fecha y hora
    new_date = date(year=int(year), month=int(month), day=int(day))
    time = datetime(year=int(year), month=int(month), day=int(day), hour=int(time.split(':')[0]), minute=int(time.split(':')[1]))
    
    print(services)
    try:
        employee = Employee.objects.get(id=employee_id)
        print(employee)
    except Employee.DoesNotExist:
        return Response({'error': 'Empleado no encontrado.'}, status=404)

    except ValueError:
        return Response({'error': 'Formato de fecha o hora inválido. Use YYYY-MM-DD y HH:MM.'}, status=400)
    
    times = Time.objects.filter(employee=employee)
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
        
    if times:
        for time_entry in times:
            start_hour_t1 = time_entry.time_start_day_one = datetime.strptime(str(time_entry.time_start_day_one), '%H:%M:%S').time()
            
            end_hour_t1 = time_entry.time_end_day_one = datetime.strptime(str(time_entry.time_end_day_one), '%H:%M:%S').time()
        
            if time_entry.time_start_day_two:
                start_hour_t2 = time_entry.time_start_day_two = datetime.strptime(str(time_entry.time_start_day_two), '%H:%M:%S').time()
                end_hour_t2 = time_entry.time_end_day_two = datetime.strptime(str(time_entry.time_end_day_two), '%H:%M:%S').time()
            
            if day_date.lower() not in [d.lower() for d in time_entry.working_days]:
                return Response({"error": "Off-agenda employee note."}, status=status.HTTP_400_BAD_REQUEST)
            
            if time_entry.double_day:
                if time.time() < start_hour_t1 or time.time() >= end_hour_t2 or time.time() < start_hour_t2 and time.time() >= end_hour_t1:
                    return Response({"error": "Time out of range."}, status=status.HTTP_400_BAD_REQUEST)
            
    if Appointment.objects.filter(date=new_date, employee=employee, time=time).exists():
        return Response({"error": "appointment date not available"}, status=status.HTTP_400_BAD_REQUEST)

    if not employee.accestoken:
        return Response({'error': 'El empleado no tiene configurada la sincronización con Google Calendar.'}, status=400)
    print(employee.accestoken)
    # Paso 2: Crear el objeto Credentials con accestoken
    credentials = Credentials(
        token=employee.accestoken,
        refresh_token=employee.token,  # Este debería ser el refresh_token guardado en la base de datos
        client_id=config('CLIENT_ID'),
        client_secret=config('CLIENTE_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )

    # Verificar si el token ha caducado y renovarlo si es necesario
    if credentials.expired:
        print("Token expirado")
        try:
            credentials.refresh(Request())  # Renueva el token
            print("Token refrescado")
            # Guarda el nuevo access_token en la base de datos
            employee.accestoken = credentials.token
            employee.save()
        except Exception as e:
            return Response({'error': f'Error al refrescar el token: {str(e)}'}, status=500)
        
    # Verificar que el token no esté vacío
    if not credentials.token:
        print("Token vacío")
        return Response({'error': 'El token de acceso no es válido.'}, status=400)

    print("Token válido")
    # Paso 3: Crear el evento en Google Calendar

    event_data = {
        'summary': 'Cita de servicio',
        'description': 'Detalles de la cita con el cliente.',  # Descripción predeterminada
        'start': {
            'dateTime': f"{new_date}T{request.data.get("time")}:00",  # Combina la fecha y hora predeterminada
            'timeZone': 'America/Bogota',  # Zona horaria
        },
        'end': {
            # Calcula la hora de finalización sumando 30 minutos a la hora de inicio
            'dateTime': f"{new_date}T{(datetime.strptime(request.data.get("time"), '%H:%M') + timedelta(minutes=30)).strftime('%H:%M')}:00",
            'timeZone': 'America/Bogota',
        },
        'attendees': [
            {'email': employee.user.email}  # Correo del empleado, asignado como valor fijo por ahora
        ],
    }

    headers = {
        'Authorization': f'Bearer {credentials.token}',
        'Content-Type': 'application/json'
    }


    start_date = "2024-11-20"
    end_date = "2024-11-20"
    print("Evento creado en Google Calendar.")
    establishment = Establisment.objects.get(employee=employee)
    schedule = Schedule.objects.create(establisment=establishment, start_date=start_date, end_date=end_date)
    client = Client.objects.get(id=client_id)
    appointment = Appointment.objects.create(
        client=client,
        employee=employee,
        date=new_date,
        time=time,
        establisment=establishment,
        estate='Pendiente',
        method='Efectivo',
        schedule= schedule
    )
    
    print("Creando evento en Google Calendar...")
    response = requests.post(
        'https://www.googleapis.com/calendar/v3/calendars/primary/events',
        headers=headers,
        json=event_data
    )
    print(response.json())

    # Verificar la respuesta
    if response.status_code != 200:
        print("Error al crear el evento en Google Calendar.")
        return Response({
            'error': 'No se pudo crear el evento en Google Calendar.',
            'details': response.json()  # Detalles del error si los hay
        }, status=500)

    print("Cita creada en la base de datos.")
    for service_id in services:
        service = Service.objects.get(id=service_id)
        appointment.services.add(service)
    
    appointment.save()

    # Retornar respuesta exitosa
    return Response({
        'message': 'Cita creada y agendada en Google Calendar exitosamente.',
    })
