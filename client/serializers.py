from rest_framework import serializers
from .models import Client

class clientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
