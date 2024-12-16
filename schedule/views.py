from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import Time
from .models import TimeException
from employee.models import Employee
from rest_framework.response import Response
from rest_framework import status
from .serializers import timeSerializer
from .serializers import timeExceptionSerializer
from datetime import datetime, timedelta

def timedelta_to_hhmmss(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"
def time_to_hhmmss(t):
        return f"{t.hour:02}:{t.minute:02}:{t.second:02}"

@api_view(['GET'])
def Times(request, employee_id):
    try:
        # Obtener datos del empleado y sus horarios
        employee = Employee.objects.get(id=employee_id)
        times = Time.objects.filter(employee=employee)
        exceptions = TimeException.objects.filter(employee=employee)
        
        if not employee_id:
            return Response({"error": "El employee_id no ha sido proporcionado"}, status=status.HTTP_404_NOT_FOUND)
        if not employee:
            return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        if not times:
            return Response({"error": "No se encontraron horarios para el empleado"}, status=status.HTTP_404_NOT_FOUND)

        # Lista para almacenar los resultados
        times_info = []

        # Iterar sobre los horarios
        for time in times:
            delta = time.date_end - time.date_start
            for day_offset in range(delta.days + 1):  # Iterar por cada día en el rango
                current_date = time.date_start + timedelta(days=day_offset)
                state = "Completa"  # Estado predeterminado
                
                # Revisar las excepciones para este día
                if current_date.day == 8:
                    print(exception.time_start, timedelta_to_hhmmss(timedelta(hours=00, minutes=00, seconds=00)), exception.time_end, timedelta_to_hhmmss(timedelta(hours=23, minutes=59, seconds=59)))
                for exception in exceptions:
                    # Verificar si la excepción afecta el día actual
                    if exception.date_start <= current_date <= exception.date_end:
                        # Caso 1: excepción afecta todo el día
                        if time.double_day:
                            if time.time_start_day_one == exception.time_start <= exception.time_end == time.time_end_day_two:
                                state = "NoLaboral"
                                break
                        else:
                            if time.time_start_day_one == exception.time_start <= exception.time_end == time.time_end_day_one:
                                state = "NoLaboral"
                                break
                        if time_to_hhmmss(exception.time_start) == timedelta_to_hhmmss(timedelta(hours=00, minutes=00, seconds=00)) and time_to_hhmmss(exception.time_end) == timedelta_to_hhmmss(timedelta(hours=23, minutes=59, seconds=59)):
                            print("entré")
                            state = "NoLaboral"
                            break
                        
                        # Caso 2: excepción afecta parcialmente
                        if exception.time_start <= time.time_start_day_one <= exception.time_end or \
                           exception.time_start <= time.time_start_day_two <= exception.time_end:
                            state = "Mixta"
                            break
                
                # Guardar el estado para este día
                time_serializer = timeSerializer(time)
                exception_serializer = timeExceptionSerializer(exception)
                times_info.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "state": state,
                    "time": time_serializer.data,
                    "exception": exception_serializer.data
                })
        
        # Responder con los resultados
        return Response({'times': times_info}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
