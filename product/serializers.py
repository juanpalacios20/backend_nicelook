from rest_framework import serializers
from .models import Product

class productSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
