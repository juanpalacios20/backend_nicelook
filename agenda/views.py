from django.shortcuts import render
from rest_framework import viewsets
from .models import Agenda
from .serializers import agendaSerializer
# Create your views here.
class agendaViewSet(viewsets.ModelViewSet):
    serializer_class = agendaSerializer
    queryset = Agenda.objects.all()
    
