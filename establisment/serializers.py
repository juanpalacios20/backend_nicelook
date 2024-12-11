from rest_framework import serializers
from .models import Establisment

class establismentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establisment
        fields = '__all__'
