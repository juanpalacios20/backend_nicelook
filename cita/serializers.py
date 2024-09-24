from rest_framework import serializers
from .models import Cita

class citaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = '__all__'
