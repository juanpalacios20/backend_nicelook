from django.shortcuts import render
from rest_framework import viewsets
from .models import Client
from .serializers import clientSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from appointment.models import Appointment
from rest_framework.response import Response
from rest_framework import status
from appointment.serializers import appointmentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth.models import User
from product_payment.models import Product_payment
from product_payment.serializers import ProductPaymentSerializer

# Create your views here.
class clientViewSet(viewsets.ModelViewSet):
    serializer_class = clientSerializer
    queryset = Client.objects.all()

@api_view(['GET'])
def client_product_purchases(request, client_id):
    try:
        purchases = Product_payment.objects.filter(client_id=client_id, state=False)
        
        purchases_serialized = ProductPaymentSerializer(purchases, many=True)
        
        return Response(
            {"data": purchases_serialized.data}, 
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': f'Error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
def client_appointment_history(request, client_id):
    
    try:
        client = Client.objects.get(id=client_id)
        appointments = Appointment.objects.filter(client=client).order_by('-date')
        
        if not appointments.exists():
            return Response({'message': 'No appointments found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = appointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_client(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
        serializer = clientSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['PUT'])
def update_client(request, client_id):
    try:
        client = Client.objects.get(id=client_id)  # Obtiene el cliente a actualizar
        data = request.data
        
        user = client.user
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.save()  

        client.phone = data.get('phone', client.phone)
        client.save()  

        # Serializa y responde
        serializer = clientSerializer(client)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClientLoginView(APIView):
    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        email = request.data.get('email')
        password = request.data.get('password')

        if token:
            # Validar el ID Token usando la API de Google
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

            # Intentar obtener o crear el usuario y el objeto Client
            user, created = User.objects.get_or_create(email=email)
            if created:
                user.username = first_name + " " + last_name + str(user.id)
                user.first_name = first_name
                user.last_name = last_name
                user.set_unusable_password()  # Ya que el usuario utiliza Google para autenticarse
                user.save()
            
            client, _ = Client.objects.get_or_create(user=user, defaults={
                'googleid': google_id,
                'token': token,
                'accestoken': token_info.get('at_hash'),
                'phone': request.data.get('phone', '')
            })

        elif email and password:
            # Intentar autenticar al usuario con email y contraseña
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            #user = authenticate(request, email= email, password=password)
            if not user:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                client = Client.objects.get(user=user)
            except Client.DoesNotExist:
                return Response({'error': 'Client account not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Provide either a Google token or email and password'}, status=status.HTTP_400_BAD_REQUEST)

        # Generar tokens de acceso (JWT)
        refresh = RefreshToken.for_user(user)
        # Agregar información adicional al token
        refresh['email'] = user.email
        refresh['first_name'] = user.first_name
        refresh['last_name'] = user.last_name
        refresh['google_id'] = client.googleid if token else None
        # Responder con el token de acceso y la información adicional
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'email': refresh.access_token.get('email'),
            'client_id': client.id
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def registerClient(request):
    try:
        # Obtener los datos de la petición
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone = request.data.get('phone')
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validar que se hayan recibido los datos
        if first_name is None or last_name is None or phone is None or email is None or password is None:
            return Response({'Error': 'No se recibieron todos los datos'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el usuario ya existe
        try:
            user = User.objects.get(email=email)
            return Response({'Error': 'Este correo ya ha sido registrado, prueba con otro'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            pass
        
        # Crear el usuario
        user = User.objects.create_user(email=email, username=email, password=password, first_name=first_name, last_name=last_name)
        user.username = first_name + " " + last_name + str(user.id)
        user.save() 
        
        # Crear el cliente
        client = Client.objects.create(user=user, phone=phone)
        return Response({'Mensaje': 'Cliente creado exitosamente', 'client_id': client.id}, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def loginClient(request):
    try:
        # Obtener los datos de la petición
        email = request.data.get("email")
        password = request.data.get("password")
        
        # Validar que se hayan recibido los datos
        if email is None or password is None:
            return Response({'Error': 'No se ha recibido el correo y la contraseña'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el usuario existe
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'Credenciales incorrectas': 'Comprueba que tus datos sean correctos e intenta de nuevo el inicio de sesión'}, status=status.HTTP_404_NOT_FOUND)
        
        # Autenticar al usuario
        user = authenticate(request, username=user.username, password=password)
        
        # Verificar si el usuario se autenticó correctamente
        if user is not None:
            try:
                client = Client.objects.get(user=user)
                return Response({'Mensaje': 'Inicio de sesión exitoso', 'client_id': client.id}, status=status.HTTP_200_OK)
            except Client.DoesNotExist:
                return Response({'Error': 'Cuenta de cliente no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        # Si el usuario no se autenticó correctamente
        else:
            return Response({'Credenciales incorrectas': 'Comprueba que tus datos sean correctos e intenta de nuevo el inicio de sesión'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Manejo de errores
    except Exception as e:
        return Response({'error': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)