from rest_framework import serializers
from .models import Agenda

class agendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agenda
        fields = '__all__'
