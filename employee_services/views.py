from rest_framework import viewsets
from .models import EmployeeServices
from .serializers import employeeServicesSerializer
# Create your views here.
class employeeServicesViewSet(viewsets.ModelViewSet):
    serializer_class = employeeServicesSerializer
    queryset = EmployeeServices.objects.all()
    
