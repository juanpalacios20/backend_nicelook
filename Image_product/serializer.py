from rest_framework import serializers
from .models import ImageProduct

class ImageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProduct
        fields = '__all__'