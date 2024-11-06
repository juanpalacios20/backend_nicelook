from rest_framework import serializers
from .models import ProductPaymentDetail
from product.serializers import productSerializer

class ProductPaymentDetailSerializer(serializers.ModelSerializer):
    product= productSerializer(read_only=True)

    class Meta:
        model = ProductPaymentDetail
        fields = ['product', 'quantity']