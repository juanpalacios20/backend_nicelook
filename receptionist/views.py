from django.shortcuts import render
from rest_framework import viewsets
from .models import Receptionist
from .serializers import receptionistSerializer
# Create your views here.
class receptionistViewSet(viewsets.ModelViewSet):
    serializer_class = receptionistSerializer
    queryset = Receptionist.objects.all()
    