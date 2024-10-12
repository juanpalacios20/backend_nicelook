from rest_framework import serializers
from .models import Employee
from django.contrib.auth.models import User

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class employeeSerializer(serializers.ModelSerializer):
    user = userSerializer()
    class Meta:
        model = Employee
        fields = '__all__'
