from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from product_payment.models import Product_payment
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
        day = request.GET.get('day')
        
        if not year or not month or not day:
            return JsonResponse({'error': 'Year and month are required parameters'}, status=400)
        
        establisment = Establisment.objects.get(id=establisment_id)

        
        employees = Employee.objects.filter(establisment=establisment)
        
        # Filtrar las citas por el establecimiento y el mes y año indicados
        
        employee_list = []
        
        # Iterar sobre los empleados y calcular ganancias
        for employee in employees:
            profit_employee = 0
            appointments = Appointment.objects.filter(
            establisment=establisment, 
            estate__icontains="Completada", 
            date__year=year, 
            date__month=month,
            date__day=day,
            employee=employee
        )
            for appointment in appointments:
                for service in appointment.services.all():
                    profit = service.price - (service.price * service.commission/100)
                    profit_employee += profit
            employee_list.append({
                'id': 1,
                'name': employee.user.username,
                'total_profit_month': profit_employee
                    })
        
        # Devolver la lista de empleados con sus ganancias
        return JsonResponse({'employees': employee_list}, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def get_services_most_sold(request, establisment_id):
    
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    try:
        establisment = Establisment.objects.get(id=establisment_id)
        services_count = {}
        services_response = []
        appointments = Appointment.objects.filter(
            establisment=establisment, 
            estate__icontains="Completada", 
            date__year=year, 
            date__month=month)
        for appointment in appointments:
            for service in appointment.services.all():
                service_name = service.name
                if service_name in services_count:
                    services_count[service_name] += 1
                else:
                    services_count[service_name] = 1
        sorted_services = sorted(services_count.items(), key=lambda x: x[1], reverse=True)
        top_3_services = sorted_services[:3]
        for service in top_3_services:
            services_response.append(f"{service[0]} = {service[1]}")
        return JsonResponse({'services_most_sold': services_response}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def get_products_most_sold(request, establisment_id):
    
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    try:
        establisment = Establisment.objects.get(id=establisment_id)
        products_count = {}
        products_response = []
        payments = Product_payment.objects.filter(
            establisment=establisment, 
            state=True, 
            date__year=year, 
            date__month=month)
        for payment in payments:
            for product in payment.products.all():
                product_name = product.name
                if product_name in products_count:
                    products_count[product_name] += 1
                else:
                    products_count[product_name] = 1
        sorted_products = sorted(products_count.items(), key=lambda x: x[1], reverse=True)
        top_3_products = sorted_products[:3]
        for product in top_3_products:
            products_response.append(f"{product[0]} = {product[1]}")
        return JsonResponse({'products_most_sold': products_response}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)