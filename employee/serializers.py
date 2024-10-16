from rest_framework import serializers
from .models import Employee
from nicelook_api.serializers import UserSerializer

class employeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Employee
        fields = '__all__'
