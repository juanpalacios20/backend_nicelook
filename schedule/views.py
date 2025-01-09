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

        # Lista para almacenar los resultados
        times_info = []

        # Procesar los horarios y sus excepciones
        for time in times:
            delta = time.date_end - time.date_start

            # Este for es para recorrer todos los dias del horario en el mes
            for day_offset in range(delta.days + 1):
                current_date = time.date_start + timedelta(days=day_offset)
                state = "Completa"
                exception_details = []

                # Verificar excepciones aplicables al día
                for exception in exceptions:
                    if exception.date_start <= current_date <= exception.date_end:
                        day_one_start = time.time_start_day_one
                        day_one_end = time.time_end_day_one
                        day_two_start = time.time_start_day_two if time.double_day else None
                        day_two_end = time.time_end_day_two if time.double_day else None

                        # Si la excepcion abarca todo el dia es un dia no laboral y en el front se muestra rojo
                        if (
                            (exception.time_start <= day_one_start and exception.time_end >= day_one_end) and
                            (not time.double_day or (exception.time_start <= day_two_start and exception.time_end >= day_two_end))
                        ):
                            state = "NoLaboral"
                        # Si la excepcion abarca un rango parcial entonces es un dia mixto y en el front se muestra amarillo    
                        elif (
                            (exception.time_start < day_one_end and exception.time_end > day_one_start) or
                            (time.double_day and exception.time_start < day_two_end and exception.time_end > day_two_start)
                        ):
                            state = "Mixta"

                        exception_details.append({"timeException": timeExceptionSerializer(exception).data})
                        

                times_info.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "state": state,
                    "time": timeSerializer(time).data,
                    "exception": exception_details,
                })

        # Procesar excepciones que no coinciden con horarios
        for exception in exceptions:
            delta = exception.date_end - exception.date_start

            for day_offset in range(delta.days + 1):
                current_date = exception.date_start + timedelta(days=day_offset)

                # Verificar si el día no está cubierto por un horario
                # Si por ejemplo tiene una cita el 20 de mayo, puede agendar esa excepcion en el calendario y aparecerá marcada en rojo 
                # a pesar de que no hay horario
                if not any(time.date_start <= current_date <= time.date_end for time in times):
                    times_info.append({
                        "date": current_date.strftime('%Y-%m-%d'),
                        "state": "Jornada no laboral",
                        "time": None,
                        "exception": timeExceptionSerializer(exception).data,
                    })

        return Response({'times': times_info}, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


