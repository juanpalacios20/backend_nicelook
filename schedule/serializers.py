from rest_framework import serializers
from .models import Time
from .models import TimeException
        
class timeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time
        fields = '__all__'
        
class timeExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeException
        fields = '__all__'
