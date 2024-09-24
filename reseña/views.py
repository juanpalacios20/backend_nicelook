from django.shortcuts import render
from rest_framework import viewsets
from .models import Reseña
from .serializers import reseñaSerializer
# Create your views here.
class reseñaViewSet(viewsets.ModelViewSet):
    serializer_class = reseñaSerializer
    queryset = Reseña.objects.all()
    