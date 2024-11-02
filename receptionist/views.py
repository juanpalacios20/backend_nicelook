from datetime import date
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import viewsets,status
from appointment.models import Appointment
from appointment.serializers import appointmentSerializer
from employee_services.models import EmployeeServices
from product_payment.models import Product_payment
from .models import Receptionist
from .serializers import receptionistSerializer
from product_payment.serializers import ProductPaymentSerializer
from rest_framework.decorators import api_view


# Create your views here.
class receptionistViewSet(viewsets.ModelViewSet):
    serializer_class = receptionistSerializer
    queryset = Receptionist.objects.all()

@api_view(["GET"]) 
def appointments(request):
    try:
        id_establisment = request.data.get('id_establisment')
        
        id_employee = request.data.get('id_employee')

        day = request.data.get('day')
        month = request.data.get('month')
        year = request.data.get('year')

        appointments_date = date(year, month, day) 
        appointments = Appointment.objects.filter(date = appointments_date, establisment=id_establisment, employee=id_employee, estate='Completada')

        total_pagar = 0
        commision= 0
        for appointment in appointments:
            total_pagar += appointment.total_price()
            commision += appointment.commision()

        serializer = appointmentSerializer(appointments, many=True)

        return Response({'appointments': serializer.data, 'total_pagar': total_pagar, 'commission': commision}, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])  
def products_sold(request):
    try:
        id_establisment = request.data.get('id_establisment')

        day = request.data.get('day')
        month = request.data.get('month')
        year = request.data.get('year')

        payment_product_date = date(year, month, day) 
        payments_product = Product_payment.objects.filter(date=payment_product_date, establisment=id_establisment)

        total_ventas= 0 
        for payment in payments_product:
            total_ventas += payment.total()

        serializer = ProductPaymentSerializer(payments_product, many=True)
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