from django.shortcuts import render
from rest_framework import viewsets
from client.models import Client
from rest_framework.response import Response
from establisment.models import Establisment
from rest_framework import status
from .models import Review
from .serializers import reviewSerializer
from rest_framework.decorators import api_view
# Create your views here.
class reviewViewSet(viewsets.ModelViewSet):
    serializer_class = reviewSerializer
    queryset = Review.objects.all()
    

@api_view(['POST'])
def create_review(request, client_id, establisment_id):
        
        try:
            establisment = Establisment.objects.get(id=establisment_id)
            autor = Client.objects.get(id=client_id)
            
            comment = request.data.get('comment')
            rating = request.data.get('rating')
            
            if Review.objects.filter(autor=autor, establisment=establisment).exists():
                return Response({'error': 'Ya has reseñado este establecimiento'}, status=status.HTTP_400_BAD_REQUEST) 
            
            if rating is None or not (0 <= float(rating) <= 5):
                return Response({'error': 'La calificación debe estar entre 0 y 5'}, status=status.HTTP_400_BAD_REQUEST)
            
            review = Review.objects.create(autor=autor, comment=comment, rating=rating, establisment=establisment)
            return Response({'success': 'Reseña creada'}, status=status.HTTP_201_CREATED)
        
        except Establisment.DoesNotExist:
            return Response({'error': 'El Establecimiento no ha sido encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Client.DoesNotExist:
            return Response({'error': 'El Cliente no ha sido encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Formato de calificación inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
@api_view(['GET'])
def get_reviews(request, establisment_id):
    
    try:
        establisment = Establisment.objects.get(id=establisment_id)
        reviews = Review.objects.filter(establisment=establisment)
        serializer = reviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    except Establisment.DoesNotExist:
        return Response({'error': 'El Establecimiento no ha sido encontrado'}, status=status.HTTP_404_NOT_FOUND)