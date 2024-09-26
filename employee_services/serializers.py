from rest_framework import serializers
from .models import EmployeeServices

class employeeServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeServices
        fields = '__all__'