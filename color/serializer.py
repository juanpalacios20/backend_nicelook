from rest_framework import serializers
from .models import Color

class colorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'