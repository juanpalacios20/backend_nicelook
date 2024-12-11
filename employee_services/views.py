from rest_framework import viewsets
from .models import EmployeeServices
from .serializers import employeeServicesSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from employee.models import Employee
# Create your views here.
class employeeServicesViewSet(viewsets.ModelViewSet):
    serializer_class = employeeServicesSerializer
    queryset = EmployeeServices.objects.all()
    
    
@api_view(['GET'])
def employeeServicesList(request, employee_id):
    try:
        # Obtener el empleado por ID
        employee = Employee.objects.get(id=employee_id)

        # Obtener los servicios asignados al empleado
        employee_services = EmployeeServices.objects.filter(employee=employee)
        
        if not employee_services.exists():
            return Response({"message": "This employee has no assigned services."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serializar los servicios
        serializer = employeeServicesSerializer(employee_services, many=True)

        # Devolver la respuesta
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['DELETE'])
def employeeServiceDelete(request, employee_id, service_id):
    try:
        # Obtener el empleado por ID
        employee = Employee.objects.get(id=employee_id)

        # Obtener el servicio por ID
        service = EmployeeServices.objects.get(employee=employee, service_id=service_id)
        
        # Eliminar la relación
        service.delete()

        # Devolver la respuesta
        return Response({"message": "Service successfully eliminated."}, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
    except EmployeeServices.DoesNotExist:
        return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e: 
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
