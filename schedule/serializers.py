from rest_framework import serializers
from .models import Time
        
class timeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time
        fields = '__all__'
