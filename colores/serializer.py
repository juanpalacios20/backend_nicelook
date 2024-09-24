from rest_framework import serializers
from .models import Colores

class coloresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colores
        fields = '__all__'