from rest_framework import serializers
from .models import EmployeeImage

class EmployeeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImage
        fields = '__all__'