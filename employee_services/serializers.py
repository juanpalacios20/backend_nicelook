from rest_framework import serializers
from .models import EmployeeServices
from service.serializers import serviceSerializer

class employeeServicesSerializer(serializers.ModelSerializer):
    service = serviceSerializer()
    class Meta:
        model = EmployeeServices
        fields = '__all__'