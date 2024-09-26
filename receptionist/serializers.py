from rest_framework import serializers
from .models import Receptionist

class receptionistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receptionist
        fields = '__all__'
