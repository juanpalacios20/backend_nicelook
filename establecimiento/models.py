from django.db import models
from servicio.models import Servicio

class Establecimiento(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(error_messages=150)
    metodos_contacto = models.CharField(max_length=50)
    servicios =  models.ManyToManyField(Servicio)

    def __str__(self):
        return self.nombre
