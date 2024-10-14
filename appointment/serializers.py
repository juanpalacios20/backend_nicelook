from rest_framework import serializers
from .models import Appointment
from client.serializers import clientSerializer
from employee.serializers import employeeSerializer
from payment.serializers import paymentSerializer
from schedule.serializers import scheduleSerializer
from service.serializers import serviceSerializer
from establisment.serializers import establismentSerializer

class appointmentSerializer(serializers.ModelSerializer):
    client = clientSerializer()
    employee = employeeSerializer()
    payment = paymentSerializer()
    services = serviceSerializer(many=True)
    schedule = scheduleSerializer()
    establisment = establismentSerializer()
    class Meta:
        model = Appointment
        fields = '__all__'
