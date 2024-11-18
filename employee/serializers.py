from rest_framework import serializers
from .models import Employee
from django.contrib.auth.models import User
from establisment.serializers import establismentSerializer
from category.serializers import categorySerializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

# Serializer para el modelo Empleado
class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    establisment = establismentSerializer()
    especialty = categorySerializer(many=True)

    class Meta:
        model = Employee
        fields = '__all__'