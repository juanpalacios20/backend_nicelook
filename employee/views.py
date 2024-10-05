from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from employee_services.models import EmployeeServices
from appointment.models import Appointment
from establisment.models import Establisment
from .models import Employee
from .serializers import employeeSerializer
import json
from rest_framework.decorators import api_view

# Create your views here.
class employeeViewSet(viewsets.ModelViewSet):
    serializer_class = employeeSerializer
    queryset = Employee.objects.all()
    
@api_view(['GET'])
def get_payment_employee(request,establisment_id):
    try:
        year = request.GET.get('year')
        month = request.GET.get('month')
        #day = request.GET.get('day')
        
        establisment = Establisment.objects.get(id=establisment_id)
        employees = Employee.objects.filter(establisment=establisment)
        appointmenst = Appointment.objects.filter(establisment=establisment,estate=False,date__year=year,date__month=month)
        
        
        employee_list = []
        
        for employee in employees:
            profit_employee = 0
            for appointment in appointmenst:
                if appointment.schedule.id == employee.schedule.id:
                    for service in appointment.service.all():
                        comission = EmployeeServices.objects.filter(employee=employee,service=service)
                        profit = service.price - (service.price * comission.commission)
                        profit_employee += profit
                        employee_list.append({
                            'id': employee.id,
                            'name': employee.user.username,
                            'total_profit_month': profit_employee
                        })
        return JsonResponse(employee_list)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)