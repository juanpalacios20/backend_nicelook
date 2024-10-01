from rest_framework import serializers
from .models import ReviewEmployee

class reviewEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewEmployee
        fields = '__all__'
