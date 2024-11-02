from rest_framework import serializers

from establisment.models import Establisment
from employee.models import Employee
from schedule.models import Schedule
from service.models import Service
from client.models import Client
from .models import Appointment
from client.serializers import clientSerializer
from employee.serializers import EmployeeSerializer
from schedule.serializers import scheduleSerializer
from service.serializers import serviceSerializer
from establisment.serializers import establismentSerializer

class appointmentSerializer(serializers.ModelSerializer):
    establisment = serializers.PrimaryKeyRelatedField(queryset=Establisment.objects.all())
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    schedule = serializers.PrimaryKeyRelatedField(queryset=Schedule.objects.all())  
    services = serviceSerializer(many=True)
    class Meta:
        model = Appointment
        fields = '__all__'
