from django.shortcuts import render
from rest_framework import viewsets

from service.models import Service
from .models import ReviewEmployee
from .serializers import reviewEmployeeSerializer
from rest_framework.decorators import api_view
from employee.models import Employee
from client.models import Client
from appointment.models import Appointment
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
class reviewEmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = reviewEmployeeSerializer
    queryset = ReviewEmployee.objects.all()
    
    
@api_view(['POST'])
def create_review(request, client_id, employee_id, appointment_id):
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        employee = Employee.objects.get(id=employee_id)
        autor = Client.objects.get(id=client_id)
        
        comment = request.data.get('comment')
        rating = request.data.get('rating')
        
        if appointment.estate != "COMPLETED":
            return Response({'error': 'The appointment must be completed to leave a review'}, status=status.HTTP_400_BAD_REQUEST)  
        
        if ReviewEmployee.objects.filter(autor=autor, appointment=appointment).exists():
            return Response({'error': 'You have already reviewed this appointment'}, status=status.HTTP_400_BAD_REQUEST) 
        
        if rating is None or not (0 <= float(rating) <= 5):
            return Response({'error': 'Rating must be between 0 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        
        review = ReviewEmployee.objects.create(autor=autor, comment=comment, rating=rating, employee=employee, appointment=appointment)
        return Response({'success': 'Review created'}, status=status.HTTP_201_CREATED)
    
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({'error': 'Invalid rating format'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
@api_view(['GET'])
def get_reviews_client(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
        reviews = ReviewEmployee.objects.filter(autor=client)
        
        # Verificar si existen reseñas
        if not reviews.exists():
            return Response({'message': 'No reviews found for this client'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serializar las reseñas
        serializer = reviewEmployeeSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)


    
    
    