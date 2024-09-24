from django.db import models
from django.contrib.auth.models import User
from servicio.models import Servicio
from agenda.models import Agenda

# Create your models here.
class Empleado (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    codigo = models.IntegerField()
    telefono = models.CharField(max_length=15)
    estado = models.BooleanField()
    especialidad = models.CharField(max_length=100)
    servicios = models.ManyToManyField(Servicio)
    agenda = models.OneToOneField(Agenda, on_delete=models.CASCADE)
    googleid = models.CharField(null=True)
    token = models.CharField(null=True)
    accestoken = models.CharField(null=True)
    
    
    def __str__ (self):
        return self.user.username