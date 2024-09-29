from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import requests

User = get_user_model()

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')

        # Enviar token a la API de Google para obtener información del usuario
        user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        headers = {'Authorization': f'Bearer {token}'}
        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code == 200:
            user_data = user_info_response.json()
            email = user_data.get('email')
            first_name = user_data.get('given_name')
            last_name = user_data.get('family_name')
            google_id = user_data.get('sub')

            # Obtener o crear el usuario en la base de datos
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )

            if created:
                # Si el usuario es creado, puede que desees enviar un correo de bienvenida u otros procesos.
                pass

            # Puedes autenticar al usuario aquí, si lo deseas
            # (opcional) login(request, user)

            return Response({'email': email, 'first_name': first_name, 'last_name': last_name, 'google_id': google_id})
        
        return Response({'error': 'Unable to authenticate'}, status=status.HTTP_400_BAD_REQUEST)
