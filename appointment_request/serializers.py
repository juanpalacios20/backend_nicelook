# serializers.py
from rest_framework import serializers
from .models import Appointment_Request
from client.models import Client
from employee.models import Employee
from service.models import Service

class AppointmentRequestSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    services = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), many=True)

    class Meta:
        model = Appointment_Request
        fields = ['client', 'employee', 'services', 'created_at', 'estate']
