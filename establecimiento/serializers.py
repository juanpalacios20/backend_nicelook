from rest_framework import serializers
from .models import Establecimiento

class establecimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establecimiento
        fields = '__all__'
