from rest_framework import serializers
from .models import ImagenEstablecimiento

class imagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenEstablecimiento
        fields = '__all__'
