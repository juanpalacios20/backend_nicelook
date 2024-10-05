from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from employee_services.models import EmployeeServices
from appointment.models import Appointment
from establisment.models import Establisment
from schedule.models import Schedule
from .models import Employee
from .serializers import employeeSerializer
import json
from rest_framework.decorators import api_view

# Create your views here.
class employeeViewSet(viewsets.ModelViewSet):
    serializer_class = employeeSerializer
    queryset = Employee.objects.all()
    
@api_view(['GET'])
def get_payment_employee(request, establisment_id):
    try:
        year = request.GET.get('year')
        month = request.GET.get('month')
        
        if not year or not month:
            return JsonResponse({'error': 'Year and month are required parameters'}, status=400)
        
        # Obtener el establecimiento y verificar si existe
        try:
            establisment = Establisment.objects.get(id=establisment_id)
        except Establisment.DoesNotExist:
            return JsonResponse({'error': 'Establishment not found'}, status=404)
        
        # Filtrar los horarios y empleados relacionados con el establecimiento
        schedules = Schedule.objects.filter(establisment=establisment)
        employees = Employee.objects.filter(schedule__in=schedules)
        
        # Filtrar las citas por el establecimiento y el mes y año indicados
        appointments = Appointment.objects.filter(
            establisment=establisment, 
            estate=False, 
            date__year=year, 
            date__month=month
        )
        
        employee_list = []
        
        # Iterar sobre los empleados y calcular ganancias
        for employee in employees:
            profit_employee = 0
            for appointment in appointments:
                if appointment.schedule.id == employee.schedule.id:
                    for service in appointment.services.all():  # Corregir `service.all()` a `services.all()`
                        try:
                            # Obtener la comisión para este empleado y servicio
                            comission = EmployeeServices.objects.get(employee=employee, service=service)
                            profit = service.price * comission.commission
                            profit_employee += profit
                        except EmployeeServices.DoesNotExist:
                            return JsonResponse({'error': f'Commission data not found for employee {employee.id} and service {service.id}'}, status=404)

            # Agregar al empleado al listado final con sus ganancias totales
            employee_list.append({
                'id': employee.id,
                'name': employee.user.username,
                'total_profit_month': profit_employee
            })
        
        # Devolver la lista de empleados con sus ganancias
        return JsonResponse({'employees': employee_list}, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
