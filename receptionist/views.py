from datetime import date
import uuid
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import viewsets,status
from appointment.models import Appointment
from appointment.serializers import appointmentSerializer
from employee.models import Employee
from product_payment.models import Product_payment
from establisment.models import Establisment
from .models import Receptionist
from .serializers import receptionistSerializer
from product_payment.serializers import ProductPaymentSerializer
from rest_framework.decorators import api_view
from employee.serializers import EmployeeSerializer


from dj_rest_auth.registration.views import SocialLoginView
import requests
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.
class receptionistViewSet(viewsets.ModelViewSet):
    serializer_class = receptionistSerializer
    queryset = Receptionist.objects.all()

@api_view(["PUT"])
def update_receptionist(request, receptionist_id):
    
    try:
        receptionist = Receptionist.objects.get(id=receptionist_id)
        
        # Fields to update
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        state = request.data.get('state')
        
        if first_name != receptionist.user.first_name:
            receptionist.user.first_name = first_name
            
        if last_name != receptionist.user.last_name:
            receptionist.user.last_name = last_name
            
        if email != receptionist.user.email:
            receptionist.user.email = email
        
        if phone != receptionist.phone:
            receptionist.phone = phone
        
        if state != receptionist.state:
            receptionist.state = state
        
        receptionist.user.save()
        receptionist.save()
        
        receptionist_serialized = receptionistSerializer(receptionist)
        
        return Response({"message": "Recepcionista actualizado", "receptionist": receptionist_serialized.data}, status=status.HTTP_200_OK)
    
    except Receptionist.DoesNotExist:
        return Response({"error": "No se encontro un recepcionista"},status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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
            total_pagar += appointment.total_price
            commision += appointment.commision

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
        ganancias_meses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        total_ventas_dia= 0 

        print("Datos obtenidos", id_establisment, day, month, year)
        payment_product_date = date(year, month, day) 
        payments_product = Product_payment.objects.filter(date__month=month ,establisment=id_establisment)
        if not payments_product:
            return Response(status=status.HTTP_404_NOT_FOUND)
        print("Calculando el total de ventas")
        for payment in payments_product:
            print("entré")
            total = payment.total_price
            print (total)
            if payment.date == payment_product_date:
                total_ventas_dia += total
                print("ostras")
            print ("tan")
            ganancias_meses[int(payment.date.month - 1)] += payment.total_price
                

        print("Serializando")
        serializer = ProductPaymentSerializer(payments_product, many=True)
        print(serializer.data)
        print("Enviando respuesta") 
        return Response({'products': serializer.data, 
                         'total': total_ventas_dia,
                         'ganancias_meses': ganancias_meses[int(month)-1]}, 
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
    
class ReceptionistLogin(SocialLoginView):
    def post(self, request, *args, **kwargs):
        token = request.data.get('token')

        # Validar el ID Token usando Google API
        token_info_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
        token_info_response = requests.get(token_info_url)

        if token_info_response.status_code != 200:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        # Si el token es válido, obtener los datos del usuario
        token_info = token_info_response.json()
        email = token_info.get('email')
        first_name = token_info.get('given_name')
        last_name = token_info.get('family_name')
        google_id = token_info.get('sub')

        # Verificar si el correo electrónico está verificado
        if not token_info.get('email_verified'):
            return Response({'error': 'Email not verified'}, status=status.HTTP_400_BAD_REQUEST)

        # Intentar obtener o crear el usuario y el objeto Receptionist
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Si no existe el usuario, crear uno nuevo
            user = User.objects.create_user(email=email, first_name=first_name, last_name=last_name)
        
        # Intentar obtener o crear el objeto Receptionist asociado al usuario
        try:
            receptionist = Receptionist.objects.get(user=user)
        except Receptionist.DoesNotExist:
            # Si no existe el objeto Receptionist, crear uno nuevo
            receptionist = Receptionist.objects.create(
                user=user,
                googleid=google_id,
                token=token,
                accestoken=token_info.get('at_hash'),
                establisment=Establisment.objects.first()
            )

        # Generar tokens de acceso (JWT)
        refresh = RefreshToken.for_user(user)

        # Agregar información adicional al token
        refresh['email'] = user.email
        refresh['first_name'] = user.first_name
        refresh['last_name'] = user.last_name
        refresh['google_id'] = google_id
        refresh['establishment'] = receptionist.establisment.id

        # Responder con el token de acceso y la información adicional
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'email': refresh.access_token.get('email'),
        }, status=status.HTTP_200_OK)
