from django.db import models

# Create your models here.

class Servicio (models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.FloatField()
    duracion = models.CharField(max_length=100)
    comision = models.FloatField()
    categoria = models.CharField(max_length=100)
    
    def __str__ (self):
        return self.nombre
    