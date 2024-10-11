from rest_framework.decorators import api_view
from rest_framework import viewsets
from employee.models import Employee
from .serializers import employeeSerializer
# Create your views here.
class employeeViewSet(viewsets.ModelViewSet):
    serializer_class = employeeSerializer
    queryset = Employee.objects.all()
