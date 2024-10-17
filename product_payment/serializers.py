from rest_framework import serializers
from .models import Product_payment

class productPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_payment
        fields = '__all__'