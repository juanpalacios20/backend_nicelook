from rest_framework import serializers
from .models import ReviewProduct

class reviewProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewProduct
        fields = '__all__'
