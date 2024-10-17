from django.shortcuts import render
from rest_framework import viewsets
from .models import Administrator
from .serializers import administratorSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.middleware.csrf import get_token

# Create your views here.
class administratorViewSet(viewsets.ModelViewSet):
    serializer_class = administratorSerializer
    queryset = Administrator.objects.all()
    
@api_view(['POST'])
def register(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=email,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password
    )
    
    Administrator.objects.create(user=user)

    user.save()
    token = Token.objects.create(user=user)
    return Response({'token': token.key}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def loginAdmin(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(email=email).first()
    
    if not user or not user.check_password(password):
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token = Token.objects.filter(user=user).first()
    if not token:
        token = Token.objects.create(user=user)
        
    csrf_token = get_token(request)
    
    return Response({'token': token.key, 'csrf_token': csrf_token}, status=status.HTTP_200_OK)