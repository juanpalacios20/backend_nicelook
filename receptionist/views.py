import uuid
from django.shortcuts import render
from rest_framework import viewsets
from establisment.models import Establisment
from .models import Receptionist
from .serializers import receptionistSerializer
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
