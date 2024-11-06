from datetime import date
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import viewsets,status
from appointment.models import Appointment
from appointment.serializers import appointmentSerializer
from employee.models import Employee
from product_payment.models import Product_payment
from .models import Receptionist
from .serializers import receptionistSerializer
from product_payment.serializers import ProductPaymentSerializer
from rest_framework.decorators import api_view
from employee.serializers import EmployeeSerializer


# Create your views here.
class receptionistViewSet(viewsets.ModelViewSet):
    serializer_class = receptionistSerializer
    queryset = Receptionist.objects.all()

@api_view(["GET"]) 
def appointments(request):
    print("Entrando a la vista")
    try:
        print("Entrando al try")
        id_establisment = request.query_params.get('id_establisment')
        code = request.query_params.get('code_employee')
        day = int(request.query_params.get('day'))
        month = int(request.query_params.get('month'))
        year = int(request.query_params.get('year'))
        print("Datos obtenidos", id_establisment, code, day, month, year)
        employee = Employee.objects.get(code=code)
        print("Creando la fecha")
        appointments_date = date(year, month, day) 
        appointments = Appointment.objects.filter(date=appointments_date, establisment=id_establisment, employee=employee, estate='Completada')
        print("Calculando el total a pagar")
        total_pagar = 0
        commision = 0
        for appointment in appointments:
            total_pagar += appointment.total_price()
            commision += appointment.commision()

        total_pagar = total_pagar - commision

        print("Serializando")
        serializer = appointmentSerializer(appointments, many=True)
        employee_serializer = EmployeeSerializer(employee)
        print("Enviando respuesta")
        return Response({"appointments": serializer.data, 'total': total_pagar, 'employee': employee_serializer.data}, status=status.HTTP_200_OK)   
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])  
def products_sold(request):
    print("Entrando a la vista")
    try:
        print("Entrando al try")
        id_establisment = request.query_params.get('id_establisment')
        day = int(request.query_params.get('day'))
        month = int(request.query_params.get('month'))
        year = int(request.query_params.get('year'))

        print("Datos obtenidos", id_establisment, day, month, year)
        payment_product_date = date(year, month, day) 
        payments_product = Product_payment.objects.filter(date=payment_product_date, establisment=id_establisment)
        if not payments_product:
            return Response(status=status.HTTP_404_NOT_FOUND)
        print("Calculando el total de ventas")
        total_ventas= 0 
        for payment in payments_product:
            total_ventas += payment.total()

        print("Serializando")
        serializer = ProductPaymentSerializer(payments_product, many=True)
        print(serializer.data)
        print("Enviando respuesta") 
        return Response({"products": serializer.data, 'total': total_ventas}, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"]) 
def create_appoinment(request):
    data = request.data
    print(data)
    serializer = appointmentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def create_sale(request):
    data= request.data
    serializer = ProductPaymentSerializer(data= data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)