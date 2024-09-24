from rest_framework import serializers
from .models import Reseña

class recepcionistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reseña
        fields = '__all__'
