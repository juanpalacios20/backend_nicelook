from rest_framework.decorators import api_view
from rest_framework import viewsets, status
from rest_framework.response import Response
from service.models import Service
from employee.models import Employee
from employee_services.models import EmployeeServices
from employee_services.serializers import employeeServicesSerializer
from .serializers import employeeSerializer
# Create your views here.
class employeeViewSet(viewsets.ModelViewSet):
    serializer_class = employeeSerializer
    queryset = Employee.objects.all()

@api_view(['POST'])
def employeeAddService(request, employee_id):
    try:
        # Obtener el empleado por ID
        employee = Employee.objects.get(id=employee_id)
        
        # Obtener el ID del servicio y el ID del establecimiento desde la solicitud
        service_id = request.data.get('service_id')
        establisment_id = request.data.get('establisment_id')
        
        # Obtener el servicio que se desea agregar
        service = Service.objects.get(id=service_id)
        
        # Verificar que el servicio pertenece al establecimiento especificado
        if service.establisment.id != establisment_id:
            return Response({"error": "The service does not belong to the establishment indicated."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que el estado del servicio sea True
        if not service.state:
            return Response({"error": "The service is not active."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya existe la relación para evitar duplicados
        if EmployeeServices.objects.filter(employee=employee, service=service).exists():
            return Response({"message": "The service is already assigned to this employee."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear la relación con la comisión del servicio
        employee_service = EmployeeServices.objects.create(
            employee=employee,
            service=service,
            commission=service.commission
        )

        # Serializar y devolver la respuesta
        serializer = employeeServicesSerializer(employee_service)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    except Service.DoesNotExist:
        return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    