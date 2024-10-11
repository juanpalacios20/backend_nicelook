from django.shortcuts import render
from rest_framework import viewsets
from .models import Establisment
from .serializers import establismentSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from service.models import Service
from service.serializers import serviceSerializer
# Create your views here.
class establismentViewSet(viewsets.ModelViewSet):
    serializer_class = establismentSerializer
    queryset = Establisment.objects.all()
    
    
@api_view(['GET'])
def servicesByEstablisment(request, establisment_id):
    try:
        # Verificar si el establecimiento existe
        establisment = Establisment.objects.get(id=establisment_id)

        # Obtener los servicios del establecimiento
        services = Service.objects.filter(establisment=establisment, state=True)

        # Serializar y devolver la respuesta
        serializer = serviceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Establisment.DoesNotExist:
        return Response({"error": "Establishment not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
