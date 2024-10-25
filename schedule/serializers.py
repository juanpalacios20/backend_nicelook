from rest_framework import serializers
from .models import Schedule
from .models import Time

class scheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'
        
class timeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time
        fields = '__all__'
