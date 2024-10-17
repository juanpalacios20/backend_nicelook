from rest_framework import serializers
from .models import Client
from django.contrib.auth.models import User

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class clientSerializer(serializers.ModelSerializer):
    user = userSerializer()
    class Meta:
        model = Client
        fields = '__all__'
