from django.shortcuts import get_object_or_404, render
import requests
from django.shortcuts import get_object_or_404, render
import requests
from rest_framework import viewsets,status
from datetime import datetime
import pytz

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
from schedule.models import Time, TimeException
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
from rest_framework.response import Response

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests
from rest_framework.decorators import api_view
from .models import Employee, Appointment, Service
from decouple import config
from django.conf import settings
from employee_services.models import EmployeeServices
from django.core.mail import send_mail
from googleapiclient.discovery import build
from receptionist.models import Receptionist

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
    

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta, date

@api_view(['PATCH'])
def reschedule(request):
    try:
        # Obtener datos de la solicitud
        id_appointment = request.data.get('id_appointment')
        day = request.data.get('day')
        month = request.data.get('month')
        year = request.data.get('year')
        time = request.data.get('time')

        if not all([id_appointment, year, month, day, time]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Construir fecha y hora de la nueva cita
        new_date = date(year=int(year), month=int(month), day=int(day))
        new_time = datetime(year=int(year), month=int(month), day=int(day),
                            hour=int(time.split(':')[0]), minute=int(time.split(':')[1]))

        # Obtener la cita existente
        try:
            appointment = Appointment.objects.get(id=id_appointment)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        employee = appointment.employee
        times = Time.objects.filter(employee=employee)
        exceptions = TimeException.objects.filter(employee=employee, date_start__lte=new_date, date_end__gte=new_date)
        appointments = Appointment.objects.filter(employee=employee, date=new_date).exclude(id=id_appointment)

        # Verificar duración total de los servicios
        services = appointment.services.all()
        total_duration = sum([EmployeeServices.objects.get(employee=employee, service=service).duration for service in services], timedelta())
        end_time = new_time + total_duration

        # Validar excepciones laborales
        if exceptions.exists():
            for exception in exceptions:
                if exception.time_start and exception.time_end:
                    exception_start = datetime.combine(new_date, exception.time_start)
                    exception_end = datetime.combine(new_date, exception.time_end)

                    if (new_time >= exception_start and new_time < exception_end) or \
                       (end_time > exception_start and end_time <= exception_end):
                        return Response({"error": "El profesional no está disponible en este horario debido a una excepción."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "El profesional no está disponible en esta fecha debido a una excepción."}, status=status.HTTP_400_BAD_REQUEST)
        
       

        # Validar horario laboral
        is_within_schedule = False
        for time_entry in times:
            if new_date < time_entry.date_start or new_date > time_entry.date_end:
                return Response({"error": "el profesional no tiene horario para este dia"}, status=status.HTTP_400_BAD_REQUEST)

            start_hour_t1 = datetime.combine(new_date, time_entry.time_start_day_one)
            end_hour_t1 = datetime.combine(new_date, time_entry.time_end_day_one)

            if time_entry.double_day:
                start_hour_t2 = datetime.combine(new_date, time_entry.time_start_day_two)
                end_hour_t2 = datetime.combine(new_date, time_entry.time_end_day_two)
            else:
                start_hour_t2 = end_hour_t2 = None

            if (start_hour_t1 <= new_time < end_hour_t1 or
                (start_hour_t2 and start_hour_t2 <= new_time < end_hour_t2)) and \
               (end_time <= end_hour_t1 or (start_hour_t2 and end_time <= end_hour_t2)):
                is_within_schedule = True
                break

        if not is_within_schedule:
            return Response({"error": "Cita fuera del horario del profesional"}, status=status.HTTP_400_BAD_REQUEST)

        # Validar conflictos con otras citas
        for existing_appointment in appointments:
            existing_start_time = existing_appointment.time
            existing_duration = sum([EmployeeServices.objects.get(employee=employee, service=service).duration
                                     for service in existing_appointment.services.all()], timedelta())
            existing_end_time = existing_start_time + existing_duration

            if (new_time >= existing_start_time and new_time < existing_end_time) or \
               (end_time > existing_start_time and end_time <= existing_end_time):
                return Response({"error": "Conflicto con otra cita ya programada"}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar la cita
        appointment.date = new_date
        appointment.time = new_time
        appointment.save()

        # Enviar notificaciones y actualizar en Google Calendar
        refresh_access_token(employee.token, employee.id)
        update_google_calendar(appointment, new_time)
        send_email_notification(appointment)

        return Response({"success": "Appointment rescheduled successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except ConnectionResetError:
        print("Client disconnected unexpectedly")
        return Response({"error": "Client disconnected unexpectedly"}, status=status.HTTP_400_BAD_REQUEST)



def update_google_calendar( appointment, time):
    """
    Actualiza un evento en Google Calendar.
    """
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import logging

    # Configurar logging para registrar errores y eventos
    logger = logging.getLogger(__name__)
    credentials = Credentials(
        token=appointment.employee.accestoken,
        refresh_token=appointment.employee.token,
        client_id=config('CLIENT_ID'),
        client_secret=config('CLIENTE_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )

    if credentials.expired:
        try:
            refresh_access_token(appointment.employee.token, appointment.employee_id)
        except Exception as e:
            return Response({'error': f'Error al refrescar el token de acceso: {str(e)}'}, status=500)
        
    if not credentials.token:
        return Response({'error': 'El token de acceso no es válido.'}, status=400)

    #Fechas de inicio y fin de la agenda (solamente para que funcione)

    try:
        # Configurar el servicio de Google Calendar
        service = build('calendar', 'v3', credentials=credentials)
        
    except Exception as e:
        logger.error(f"Error al inicializar el servicio de Google Calendar: {str(e)}")
        raise Exception(f"Error al inicializar el servicio de Google Calendar: {str(e)}")

    # Datos para actualizar el evento
    event_id = appointment.event_id
    print(event_id)  # Asegúrate de almacenar el ID del evento en tu modelo
    if not event_id:
        logger.error("El appointment no tiene un 'event_id' asignado.")
        raise Exception("El appointment no tiene un 'event_id' asignado.")
    
    start_time = time.isoformat()
    end_time = (time + timedelta(hours=1)).isoformat()  # Ajusta la duración según sea necesario

    # Obtener nombres de los servicios
    try:
        services = appointment.services.all()  # Asumiendo una relación ManyToMany
        service_names = ", ".join([service.name for service in services])
    except Exception as e:
        logger.error(f"Error al obtener servicios asociados al appointment: {str(e)}")
        raise Exception(f"Error al obtener servicios asociados al appointment: {str(e)}")

    # Construir el cuerpo del evento
    event_body = {
        'start': {'dateTime': start_time, 'timeZone': 'America/Bogota'},
        'end': {'dateTime': end_time, 'timeZone': 'America/Bogota'},
        'summary': f'Cita: {service_names}',
        'description': f'Cita reagendada. Servicios: {service_names} - Fecha: {appointment.date}\n - Hora: {appointment.time}\n - Precio total: {appointment.total_price}',
        'attendees': [
            {'email': appointment.client.user.email},
            {'email': appointment.employee.user.email},
        ],
    }
    
    try:
        if appointment.estate == "Cancelada":
            # Crear un nuevo evento si no existe
            response = service.events().insert(calendarId='primary', body=event_body).execute()
            
            # Actualizar el ID del evento y cambiar el estado de la cita
            appointment.event_id = response['id']
            appointment.estate = "Pendiente"
            appointment.save()
            print(appointment.estate)

            # Preparar el correo de notificación
            subject = "Cita Reprogramada"
            services = appointment.services.all()
            service_names = ", ".join([service.name for service in services])
            message = (
                f"Hola,\n\n"
                f"Le informamos que su cita ha sido reprogramada. La nueva fecha es el {appointment.date.strftime('%Y-%m-%d')} a las {appointment.time.strftime('%H:%M')}.\n\n"
                f"Servicios: {service_names}\n"
                f"Precio total: {appointment.total_price}\n\n"
                f"Si tienes alguna pregunta, no dudes en contactarnos.\n"
                f"Atentamente,\n"
                f"Equipo de Nicelook"
            )

            # Enviar correo a los destinatarios
            recipients = [appointment.client.user.email, appointment.employee.user.email]
            send_mail(subject,  message, settings.EMAIL_HOST_USER, recipients)

            # Log de éxito
            logger.info(f"Nuevo evento creado en Google Calendar con ID: {response['id']}")
            return response
    except Exception as e:
        # Capturar cualquier excepción y loguearla
        logger.error(f"Error al crear el evento o al procesar la cita: {e}")
        # Puedes optar por lanzar la excepción nuevamente o manejarla según sea necesario
        raise e


    # Intentar actualizar el evento
    try:
        response = service.events().update(calendarId='primary', eventId=event_id, body=event_body).execute()
        logger.info(f"Evento actualizado en Google Calendar con ID: {event_id}")
        return response
    except HttpError as http_err:
        logger.error(f"HTTPError al actualizar el evento en Google Calendar: {http_err}")
        raise Exception(f"Error HTTP al actualizar el evento: {http_err}")
    except Exception as e:
        logger.error(f"Error inesperado al actualizar el evento: {str(e)}")
        raise Exception(f"Error inesperado al actualizar el evento: {str(e)}")

def send_email_notification(appointment):
    """
    Envía un correo electrónico al cliente y al empleado notificando la nueva fecha.
    """
    # Obtener nombres de los servicios
    services = appointment.services.all()
    service_names = ", ".join([service.name for service in services])

    subject = "Cita Reprogramada"
    message = (
        f"Hola {appointment.client.user.first_name},\n\nTu cita ha sido reprogramada.\n\n"
        f"Servicios: {service_names}\n"
        f"Te esperamos el {appointment.date.strftime('%Y-%m-%d')} a las {appointment.time.strftime('%H:%M')}.\n\n"
        f"Profesional: {appointment.employee.user.first_name}\n"
        f"Precio total: {appointment.total_price}\n\n"
        f"Si tienes alguna pregunta, no dudes en contactarnos.\n\n"
        "Gracias por usar nuestro servicio."
    )
    recipients = [appointment.client.user.email, appointment.employee.user.email]
    

    send_mail(subject, message, settings.EMAIL_HOST_USER , recipients)
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
            cancel_google_calendar_event(appointment, appointment.employee)
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
    time_entries = Time.objects.filter(employee_id=employee_id)
    available_slots = []

    for entry in time_entries:
        # Comprueba si el día solicitado está en los días laborables del empleado
        #if date.strftime("%A") in entry.working_days:
            # Genera los horarios del primer turno del día
           # start_time = datetime.combine(date, entry.time_start_day_one)
           # end_time = datetime.combine(date, entry.time_end_day_one)
           # available_slots += generate_time_slots(start_time, end_time)

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

    print(f"Free slots: {free_slots}")
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

def refresh_access_token(refresh_token, employeeId):
    try:
        employee = Employee.objects.get(id=employeeId)
    except Employee.DoesNotExist:
        return "Empleado no encontrado."

    url = 'https://oauth2.googleapis.com/token'
    data = {
        'client_id': config('CLIENT_ID'),
        'client_secret': config('CLIENTE_SECRET'),
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error al comunicarse con Google: {str(e)}"

    response_data = response.json()

    if 'access_token' not in response_data:
        error_message = response_data.get("error_description", "No se recibió access_token.")
        return f"Error al refrescar el token: {error_message}"
    
    employee.accestoken = response_data['access_token']
    employee.save()
    
    return response_data['access_token']

@api_view(['POST'])
@csrf_exempt
def create_appointment(request):
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
    
    #Validamos que los campos requeridos estén presentes en la base de datos
    try:
        employee = Employee.objects.get(id=employee_id)
        client = Client.objects.get(id=client_id)
        times = Time.objects.filter(employee=employee)
        exceptions = TimeException.objects.filter(employee=employee)
        establishment = Establisment.objects.get(employee=employee)
    except Employee.DoesNotExist:
        return Response({'error': 'Empleado no encontrado.'}, status=404)
    except Client.DoesNotExist:
        return Response({'error': 'Cliente no encontrado.'}, status=404)
    except Time.DoesNotExist:
        return Response({'error': 'Horario no encontrado.'}, status=404)
    except ValueError:
        return Response({'error': 'Formato de fecha o hora inválido. Use YYYY-MM-DD y HH:MM.'}, status=400)
    
    services_list = []
    duration = []
    for service_id in services:
        try:
            service = EmployeeServices.objects.get(employee=employee, service=service_id)
            services_list.append(service.service)
            duration.append(service.duration)
        except Service.DoesNotExist:
            return Response({'error': 'Servicio no encontrado.'}, status=404)
    
    start_time = datetime.strptime(request.data.get('time'), '%H:%M')
    
    duration_total = sum(duration, timedelta())
    
    final_time = start_time + duration_total
    
    appointments = Appointment.objects.filter(employee=employee, date=new_date, estate="Pendiente")
    
    if Appointment.objects.filter(date=new_date, employee=employee_id, time=time, estate="Pendiente").exists():
        return Response({"error": "Ya se ha reservado una cita a esta hora"}, status=status.HTTP_400_BAD_REQUEST)
        
    print("Validando disponibilidad de horario 1")
        
    #Validamos que la fecha y hora estén dentro del rango permitido
    if times:
        exception1 = True
        exception2 = True
        exception3 = True
        exception4 = True
        exception5 = True
        exception6 = True
        exception7 = True
        exception8 = True
        exception9 = True
        exception10 = True
        exception11 = True
        
        for time_entry in times:
            start_hour_t1 = time_entry.time_start_day_one = datetime.strptime(str(time_entry.time_start_day_one), '%H:%M:%S').time()  
            end_hour_t1 = time_entry.time_end_day_one = datetime.strptime(str(time_entry.time_end_day_one), '%H:%M:%S').time()
            if time_entry.time_start_day_two:
                start_hour_t2 = time_entry.time_start_day_two = datetime.strptime(str(time_entry.time_start_day_two), '%H:%M:%S').time()
                end_hour_t2 = time_entry.time_end_day_two = datetime.strptime(str(time_entry.time_end_day_two), '%H:%M:%S').time()
            
            if exception1:
                if int(time_entry.date_end.month) < int(new_date.month) and int(time_entry.date_end.day) < int(new_date.day) or int(time_entry.date_end.year) < int(new_date.year) or int(new_date.month) >= int(time_entry.date_end.month) + 2:
                    exception1 = True
                else:
                    exception1 = False
            if exception2:
                if time_entry.date_end < new_date or time_entry.date_start > new_date:
                    exception2 = True
                else:
                    exception2 = False
            if time_entry.double_day:
                if exception3:
                    if time.time() < start_hour_t1:
                        exception3 = True
                    else:
                        exception3 = False
                if exception4:
                    if time.time() >= end_hour_t2:
                        exception4 = True
                    else:
                        exception4 = False
                if exception5:
                    if time.time() >= end_hour_t1 and time.time() < start_hour_t2:
                        exception5 = True
                    else:
                        exception5 = False
            else:
                exception3 = False
                exception4 = False
                exception5 = False
            if exceptions:
                for exception in exceptions:
                    if exception6:
                        if exception.date_end:
                            if exception.date_start <= new_date and exception.date_end >= new_date:
                                exception6 = True
                            else:
                                exception6 = False
                        else:
                            if exception.date_start == new_date:
                                exception6 = True
                            else:
                                exception6 = False
            else:
                exception6 = False

        if exception1:
            return Response({"error": "La cita no puede ser agendada porque el artista no tiene turno ese dia pero tienes la opción de solicitar turno con el artista."}, status=status.HTTP_400_BAD_REQUEST)
        if exception2:
            return Response({"error": "La cita no puede ser agendada porque el artista no tiene turno ese dia."}, status=status.HTTP_400_BAD_REQUEST)
        if exception3:
            return Response({"error": "La cita no puede empezar antes de el horario del artista."}, status=status.HTTP_400_BAD_REQUEST)
        if exception4:
            return Response({"error": "La cita no puede empezar despues de el horario del artista."}, status=status.HTTP_400_BAD_REQUEST)
        if exception5:
            return Response({"error": "La cita no puede ser agendada por fuera de el horario del artista."}, status=status.HTTP_400_BAD_REQUEST)
        if exception6:
            return Response({"error": "La cita no puede ser agendada porque el artista no trabaja en ese horario por motivos personales"}, status=status.HTTP_400_BAD_REQUEST)
        
    print("Validando disponibilidad de horario 2")
    if appointments:
        for appointment in appointments:
            appointment_start_time = appointment.time
            
            for service in appointment.services.all():
                services = EmployeeServices.objects.filter(employee=employee_id, service=service)
            duration_total = timedelta()
            
            for service in services:
                duration_total = service.duration
                
            appointment_end_time = (appointment.time + duration_total)
            
            if exception8:
                if start_time.time() >= appointment_start_time.time() and start_time.time() < appointment_end_time.time():
                    exception8 = True
                else:
                    exception8 = False
                
            if exception9:
                if final_time.time() > appointment_start_time.time() and final_time.time() <= appointment_end_time.time():
                    exception9 = True
                else:
                    exception9 = False
            
            for time1 in times:
                if exception10:
                    if final_time.time() >= time1.time_end_day_two:
                        exception10 = True
                    else:
                        exception10 = False
                    
                if exception11:
                    if final_time.time() >= time1.time_end_day_one:
                        exception11 = True
                    else:
                        exception11 = False

            print("exceptions")
            if exceptions:
                for exception in exceptions:
                    print("pa ver si entla", exception)
                    if exception7:
                        if new_date >= exception.date_start and new_date <= exception.date_end:
                            print("entré aunque no deberia entrar")
                            if final_time.time() <= exception.time_end and final_time.time() >= exception.time_start or appointment_start_time.time() <= exception.time_end and appointment_start_time.time() >= exception.time_start:
                                exception7 = True
                            else:
                                exception7 = False
            else:
                exception7 = False
    else: 
        exception7 = False
        exception8 = False
        exception9 = False
        exception10 = False
        exception11 = False
    if exception7:
        return Response({"error": "La cita no puede ser agendada porque el artista no trabaja en ese horario por motivos personales"}, status=status.HTTP_400_BAD_REQUEST)
    if exception8:
        return Response({'error': 'No es posible agendar la cita porque la hora de inicio interfiere con una cita que ya esta programada'}, status=status.HTTP_400_BAD_REQUEST)
    if exception9:
        return Response({'error': 'No es posible agendar la cita porque la hora de finalización interfiere con una cita que ya esta programada'}, status=status.HTTP_400_BAD_REQUEST)
    if exception10:
        return Response({'error': 'No es posible agendar la cita porque la hora de finalización interfiere con el horario laboral del artista'}, status=status.HTTP_400_BAD_REQUEST)
    if exception11:
        return Response({'error': 'No es posible agendar la cita porque la hora de finalización interfiere con el horario laboral del artista'}, status=status.HTTP_400_BAD_REQUEST)
    if not employee.token:
        return Response({'error': 'El artista no tiene configurada la sincronización con Google Calendar.'}, status=status.HTTP_400_BAD_REQUEST)
    
    print("Validando disponibilidad de horario 3")
    refresh_access_token(employee.token, employee_id)
    
    credentials = Credentials(
        token=employee.accestoken,
        refresh_token=employee.token,
        client_id=config('CLIENT_ID'),
        client_secret=config('CLIENTE_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )
        
    if not credentials.token:
        return Response({'error': 'El token de acceso no es válido.'}, status=400)

    #Fechas de inicio y fin de la agenda (solamente para que funcione)
    start_date = "2024-11-20"
    end_date = "2024-11-20"
    
    try:
        print("Creando cita")
        print("Datos")
        print("Cliente", client)
        print("Empleado", employee)
        print("Fecha", new_date)
        print("Hora", time)
        print("Establecimiento", establishment)
        print("Estado", "Pendiente")
        appointment = Appointment.objects.create(
            client=client,
            employee=employee,
            date=new_date,
            time=time,
            establisment=establishment,
            estate='Pendiente',
            method='Efectivo',
        )
        print("Cita creada", appointment)
    except Exception as e:
        return Response({'error': f'Error al crear la cita: {str(e)}'}, status=500)
    
    print("Validando disponibilidad de horario 4")
    try:
        for service in services_list:
            appointment.services.add(service) 
    except Service.DoesNotExist:
        return Response({'error': 'Servicio no encontrado.'}, status=404)
    
    try:
        services_details = "\n".join([f"- {service.name}: ${service.price}" for service in services_list])
        event_description = (
            f"Detalles de la cita:\n\n"
            f"Cliente: {client.user.first_name} {client.user.last_name}\n"
            f"Correo del cliente: {client.user.email}\n\n"
            f"Profesional: {employee.user.first_name} {employee.user.last_name}\n"
            f"Correo del profesional: {employee.user.email}\n\n"
            f"Servicios:\n{services_details}\n\n"
            f"Precio total: {appointment.total_price}\n\n"
            f"Establecimiento: {establishment.name}\n"
            f"Dirección: {establishment.address}\n"
        )
        event_data = {
                'summary': f'Cita en {establishment.name}',
                'description': event_description,
                'start': {
                    'dateTime': f"{new_date}T{request.data.get("time")}:00",
                    'timeZone': 'America/Bogota',
                },
                'end': {
                    'dateTime': f"{new_date}T{(final_time).strftime('%H:%M')}:00",
                    'timeZone': 'America/Bogota',
                },
                'attendees': [
                    {'email': employee.user.email},
                    {'email': client.user.email},
                ],
        }

        headers = {
                'Authorization': f'Bearer {credentials.token}',
                'Content-Type': 'application/json'
        }
            
        response = requests.post(
                'https://www.googleapis.com/calendar/v3/calendars/primary/events',
                headers=headers,
                json=event_data
        )

        if response.status_code != 200:
            Appointment.objects.get(id=appointment.id).delete()
            return Response({
                'error': 'No se pudo crear el evento en Google Calendar.',
                'details': response.json()
        }, status=500)
        
        else:
            print("Evento creado")
            event_id = response.json().get('id')
            appointment.event_id = event_id
            appointment.save()
            subject = f"Cita en {establishment.name}"
            message = (
                f"Hola,\n\n"
                f"Se ha agendado una cita en {establishment.name}. Aquí tienes los detalles:\n\n"
                f"Cliente: {client.user.first_name} {client.user.last_name}\n"
                f"Correo del cliente: {client.user.email}\n\n"
                f"Profesiona {employee.user.first_name} {employee.user.last_name}\n"
                f"Correo del profesional: {employee.user.email}\n\n"
                f"Servicios:\n{services_details}\n\n"
                f"Precio total: ${appointment.total_price}\n\n"
                f"Establecimiento: {establishment.name}\n"
                f"Dirección: {establishment.address}\n\n"
                f"Fecha: {new_date.strftime('%Y-%m-%d')}\n"
                f"Hora: {request.data.get('time')}\n\n"
                "Si tienes alguna pregunta, no dudes en contactarnos.\n\n"
                "Atentamente,\n"
                "Equipo de Nicelook"
            )

            recipients = [client.user.email, employee.user.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipients, fail_silently=False)
            print("Correo enviado")
    except Exception as e:
        return Response({'error': f'Error al crear el evento en Google Calendar: {str(e)}'}, status=500)

    appointment.save()
    
    # Retornar respuesta exitosa
    return Response({
        'message': 'Cita creada y agendada en Google Calendar exitosamente.',
    })

@api_view(['PATCH'])
def cancel_appointments_day(request):
    try:
        id_employee = request.data.get('id_employee')
        employee = Employee.objects.get(id=id_employee)
        establisment = Establisment.objects.get(employee=employee)
        receptionist = Receptionist.objects.get(establisment =  establisment)
        day = request.data.get('day')
        month = request.data.get('month')
        year = request.data.get('year')
        # Obtener citas para el día y mes proporcionados
        appointments = Appointment.objects.filter(date__day=day, date__month=month, date__year=year, employee=employee)
        users=[]



        # Cancelar citas
        for appointment in appointments:
            appointment.estate = "Cancelada"
            appointment.save()
            subject = "Cita cancelada"
            users.append(appointment.client.user)
            cancel_google_calendar_event(appointment.event_id, appointment.employee)

            message = (
                f"Hola {appointment.client.user.first_name},\n\n"
                f"Lamentamos informarte que el profesional {appointment.employee.user.first_name} ha cancelado tu cita en {appointment.establisment.name} para el {appointment.date.strftime('%Y-%m-%d')} a las {appointment.time.strftime('%H:%M')}n\n"
                f"prontamente te contactaremos para realizar la reprogramación de tu cita.\n\n"
                f"Si tienes alguna pregunta, no dudes en contactarnos.\n"
                f"Atentamente,\n"
                f"Equipo de Nicelook"

            )

            send_mail(subject, message, settings.EMAIL_HOST_USER , [appointment.client.user.email], fail_silently=False)
        

        subject = f"Citas del profesional {employee.user.first_name} del dia {day}/{month}/{year} canceladas"

        message = (
        f"Hola {receptionist.user.first_name},\n\n"
        f"Las citas del profesional {employee.user.first_name} del día {day}/{month}/{year} han sido canceladas.\n\n"
        f"Te recomendamos comunicarte con los siguientes clientes para reagendar sus citas canceladas:\n\n"
    )

        for user in users:
            message += (
                f"{user.first_name} {user.last_name}\n"
                f"Correo: {user.email}\n\n"
            )

        message += (
            f"Si tienes alguna pregunta, no dudes en contactarnos.\n"
            f"Atentamente,\n"
            f"Equipo de Nicelook"
        )

        send_mail(subject, message, settings.EMAIL_HOST_USER , [receptionist.user.email], fail_silently=False)
        

        return Response({'message': 'Citas canceladas exitosamente.'}, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=400)

def cancel_google_calendar_event(appointment, user):
    try:
        credentials = Credentials(
            token=user.accestoken,
            refresh_token=user.token,
            client_id=config('CLIENT_ID'),
            client_secret=config('CLIENTE_SECRET'),
            token_uri='https://oauth2.googleapis.com/token'
        )
        service = build('calendar', 'v3', credentials=credentials)
        service.events().delete(calendarId='primary', eventId=appointment.event_id).execute()
        print(f"Evento con ID {appointment.event_id} cancelado exitosamente.")
        subject = "Cita cancelada"
        message = (
            f"Hola,\n\n"
            f"Lamentamos informarte que tu cita para el {appointment.date.strftime('%Y-%m-%d')} a las {appointment.time.strftime('%H:%M')} ha sido cancelada.\n\n"
            f"Si tienes alguna pregunta, no dudes en contactarnos.\n"
            f"Atentamente,\n"
            f"Equipo de Nicelook"
        )
        recipients = [appointment.client.user.email, appointment.employee.user.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER , recipients)
    except Exception as e:
        print(f"Error al cancelar el evento {appointment.event_id}: {e}")

@api_view(['PATCH'])
def client_cancel_appointment(request):
    try:
        # Obtén el ID de la cita del cuerpo de la solicitud
        id_appointment = request.data.get('id_appointment')
        if not id_appointment:
            return Response({'error': 'El ID de la cita es requerido.'}, status=400)
        
        # Busca la cita
        appointment = Appointment.objects.get(id=id_appointment)
        
        # Configurar la zona horaria de Colombia
        colombia_tz = pytz.timezone('America/Bogota')
        
        # Obtener la hora actual con zona horaria
        actual_datetime = datetime.now(colombia_tz)
        print(f"Hora actual en Colombia: {actual_datetime}")
        
        # Asegúrate de que `appointment.time` sea timezone-aware
        if appointment.time.tzinfo is None:
            # Si no tiene zona horaria, la añadimos
            appointment_datetime = colombia_tz.localize(appointment.time)
        else:
            # Si ya tiene zona horaria, lo usamos directamente
            appointment_datetime = appointment.time
        
        print(f"Hora de la cita: {appointment_datetime}")
        
        # Verifica si faltan más de 1 hora
        if appointment_datetime - actual_datetime <= timedelta(hours=1):
            return Response({'error': 'No puedes cancelar una cita con menos de 1 hora de anticipación.'}, status=400)
        
        # Cambia el estado de la cita y guarda
        appointment.estate = "Cancelada"
        appointment.save()
        
        # Llama a la función para cancelar en Google Calendar
        cancel_google_calendar_event(appointment, appointment.employee)
        
        return Response({'message': 'Cita cancelada exitosamente.'}, status=200)
    
    except Appointment.DoesNotExist:
        return Response({'error': 'La cita no existe.'}, status=404)
    except Exception as e:
        return Response({'error': f'Error interno: {str(e)}'}, status=500)
    

@api_view(['GET'])
def get_appointments_pending(rquest, client_id):
    try:
        client = Client.objects.get(id=client_id)
        appointments = Appointment.objects.filter(client=client, estate="Pendiente")
        serializer = appointmentSerializer(appointments, many=True)
        return Response({'appointments': serializer.data}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
        
