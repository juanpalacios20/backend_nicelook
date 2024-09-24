from django.db import models
from agenda.models import Agenda
from servicio.models import Servicio
from cliente.models import Cliente

# Create your models here.

class Cita (models.Model):
    fecha = models.DateField()
    hora = models.DateTimeField()
    estado = models.BooleanField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servicios = models.ManyToManyField(Servicio)
    agenda = models.OneToOneField(Agenda, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.hora
    