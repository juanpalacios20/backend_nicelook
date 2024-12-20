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
        employee = Employee.objects.get(id=employee_id)
        times = Time.objects.filter(employee=employee)
        exceptions = TimeException.objects.filter(employee=employee)

        if not times.exists():
            return Response({"error": "No se encontraron horarios para el empleado"}, status=status.HTTP_404_NOT_FOUND)

        # Lista para almacenar los resultados
        times_info = []

        # Iterar sobre los horarios
        for time in times:
            delta = time.date_end - time.date_start

            # Iterar por cada día dentro del rango de fechas
            for day_offset in range(delta.days + 1):
                current_date = time.date_start + timedelta(days=day_offset)
                state = "Completa"  # Estado predeterminado
                exception_details = None

                # Verificar si hay excepciones para este día
                for exception in exceptions:
                    # Verifica si la excepción afecta el rango de fechas del horario laboral
                    if exception.date_start <= current_date <= exception.date_end:
                        
                        # Definimos los horarios del primer día y, si aplica, del segundo día
                        day_one_start = time.time_start_day_one
                        day_one_end = time.time_end_day_one
                        day_two_start = time.time_start_day_two if time.double_day else None
                        day_two_end = time.time_end_day_two if time.double_day else None

                        # Caso 1: NoLaboral - Excepción cubre completamente los horarios de trabajo
                        if (
                            (exception.time_start <= day_one_start and exception.time_end >= day_one_end) and
                            (not time.double_day or (exception.time_start <= day_two_start and exception.time_end >= day_two_end))
                        ):
                            state = "NoLaboral"

                        # Caso 2: Mixta - Excepción afecta parcialmente los horarios de trabajo
                        elif (
                            (exception.time_start < day_one_end and exception.time_end > day_one_start) or
                            (time.double_day and exception.time_start < day_two_end and exception.time_end > day_two_start)
                        ):
                            state = "Mixta"

                        # Caso 3: Jornada Completa - La excepción no afecta el horario laboral
                        else:
                            state = "Jornada Completa"
                        
                        # Serialización de los detalles de la excepción
                        exception_details = timeExceptionSerializer(exception).data
                        break  # Salir del ciclo al encontrar la excepción aplicable

                times_info.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "state": state,
                    "time": timeSerializer(time).data,
                    "exception": exception_details
                })

        # Responder con los resultados
        return Response({'times': times_info}, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

