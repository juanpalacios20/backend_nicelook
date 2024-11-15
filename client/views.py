from django.shortcuts import render
from rest_framework import viewsets
from .models import Client
from .serializers import clientSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth.models import User

# Create your views here.
class clientViewSet(viewsets.ModelViewSet):
    serializer_class = clientSerializer
    queryset = Client.objects.all()

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
        }, status=status.HTTP_200_OK)