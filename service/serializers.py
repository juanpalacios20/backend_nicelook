from rest_framework import serializers
from .models import Service
from category.models import Category

class categorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class serviceSerializer (serializers.ModelSerializer):
    category = categorySerializer()
    class Meta:
        model = Service
        fields = '__all__'
        