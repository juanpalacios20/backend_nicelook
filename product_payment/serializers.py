from rest_framework import serializers
from .models import Product_payment, Product_quantity

class productPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_payment
        fields = '__all__'

class productQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_quantity
        fields = '__all__'