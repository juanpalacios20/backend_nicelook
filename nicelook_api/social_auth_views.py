from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import requests
from administrator.models import Administrator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response


User = get_user_model()

class GoogleLogin(SocialLoginView):
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

        # Obtener o crear el usuario en la base de datos
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )

        if created:
            # Crear un administrador si el usuario es nuevo
            Administrator.objects.create(user=user)

        # Generar tokens de acceso (JWT)
        refresh = RefreshToken.for_user(user)

        # Agregar información adicional al token
        refresh['email'] = user.email
        refresh['first_name'] = user.first_name
        refresh['last_name'] = user.last_name
        refresh['google_id'] = google_id


        # Responder con el token de acceso y la información adicional
        return Response({
            'access_token': str(refresh.access_token),  # Token de acceso con información del usuario
            'refresh_token': str(refresh),
            'email': refresh.access_token.get('email'), # Token de refresco
        }, status=status.HTTP_200_OK)