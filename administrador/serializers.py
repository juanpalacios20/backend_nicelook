from rest_framework import serializers
from .models import Administrador

class administradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrador
        fields = '__all__'
