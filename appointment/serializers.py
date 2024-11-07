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
    client = clientSerializer()
    employee = EmployeeSerializer()
    services = serviceSerializer(many=True)
    schedule = scheduleSerializer()
    establisment = establismentSerializer()
    total_price = serializers.ReadOnlyField()
    commision = serializers.ReadOnlyField()
    class Meta:
        model = Appointment
        fields = [
            'id',
            'establisment',
            'date',
            'time',
            'estate',
            'client',
            'employee',
            'services',
            'schedule',
            'method',
            'total_price',
            'commision'
        ]