from rest_framework import serializers
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
    class Meta:
        model = Appointment
        fields = '__all__'
from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    time_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ('id', 'date', 'time', 'time_formatted', 'estate', 'client', 'employee', 'services', 'schedule', 'total')

    def get_time_formatted(self, obj):
        return obj.time.strftime("%H:%M:%S")