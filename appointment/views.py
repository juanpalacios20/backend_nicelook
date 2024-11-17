from django.shortcuts import render
from rest_framework import viewsets,status
from .models import Appointment
from .serializers import appointmentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date
from datetime import datetime
from schedule.models import Time

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
        time = datetime(year=int(year), month=int(month), day=int(day), hour=int(time.split(':')[0]), minute=int(time.split(':')[1]))
        print(day, month, year, time)

        if not id_appointment or not day or not month or not year:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener la cita existente
        appointment = Appointment.objects.get(id=id_appointment)

        new_date = date(year=int(year), month=int(month), day=int(day))
        print(new_date)
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

        if Appointment.objects.filter(date=new_date, establisment=appointment.establisment, employee=appointment.employee, time = time).exists():
            return Response({"error": "appointment date not available"}, status=status.HTTP_400_BAD_REQUEST)
        
        time_employee = Time.objects.filter(employee=appointment.employee)
        if time_employee:
            for t in time_employee:
                if day_date.lower() not in [d.lower() for d in t.working_days]:
                    return Response({"error": "Off-agenda employee note."}, status=status.HTTP_400_BAD_REQUEST)
        
        if appointment.estate == "Completada" or appointment.estate == "Cancelada":
            return Response({"error": "appointment canceled or completed"}, status=status.HTTP_400_BAD_REQUEST)

        appointment.date = new_date
        # Si se proporciona un nuevo tiempo, actualizarlo
        if time:
            appointment.time = time
        if time:
            for time_entry in time_employee:
                start_hour_t1 = time_entry.time_start_day_one = datetime.strptime(str(time_entry.time_start_day_one), '%H:%M:%S').time()

                end_hour_t1 = time_entry.time_end_day_one = datetime.strptime(str(time_entry.time_end_day_one), '%H:%M:%S').time()

                if time_entry.time_start_day_two:
                    start_hour_t2 = time_entry.time_start_day_two = datetime.strptime(str(time_entry.time_start_day_two), '%H:%M:%S').time()
                    end_hour_t2 = time_entry.time_end_day_two = datetime.strptime(str(time_entry.time_end_day_two), '%H:%M:%S').time()

                if day_date.lower() not in [d.lower() for d in time_entry.working_days]:
                    return Response({"error": "Off-agenda employee note."}, status=status.HTTP_400_BAD_REQUEST)

                if time_entry.double_day:
                    if time.time() < start_hour_t1 or time.time() > end_hour_t2 or time.time() < start_hour_t2 and time.time() > end_hour_t1:
                        return Response({"error": "Time out of range."}, status=status.HTTP_400_BAD_REQUEST)
        # Guardar los cambios
        appointment.save()

        return Response({"success": "Appointment rescheduled"},status=status.HTTP_200_OK)
    
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
        
        
        