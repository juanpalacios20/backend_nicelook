from rest_framework import serializers
from .models import Recepcionista

class recepcionistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recepcionista
        fields = '__all__'
