from rest_framework import serializers
from .models import Review
from client.models import Client
from client.serializers import clientSerializer

class reviewSerializer(serializers.ModelSerializer):
    autor = clientSerializer()
    class Meta:
        model = Review
        fields = '__all__'
