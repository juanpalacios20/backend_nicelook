from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import Time
from .models import TimeException
from employee.models import Employee
from rest_framework.response import Response
from rest_framework import status
from .serializers import timeSerializer
from .serializers import timeExceptionSerializer

@api_view(['GET'])    
def Times(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        times = Time.objects.filter(employee=employee)
        exceptiones = TimeException.objects.filter(employee=employee)
        times_info = []
        exceptions_info = []
    
        if not employee_id:
            return Response({"error": "el employee_id no ha sido proporcionado"}, status=status.HTTP_404_NOT_FOUND)
        if not employee:
            return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        if not times:
            return Response({"error": "No se encontraron horarios para el empleado"}, status=status.HTTP_404_NOT_FOUND)
        
        for time in times:
            serializer = timeSerializer(time)
            times_info.append(serializer.data)
            
        for exception in exceptiones:
            serializer = timeExceptionSerializer(exception) 
            exceptions_info.append(serializer.data)
        
        return Response({'times': times_info, 'exceptions': exceptions_info}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)