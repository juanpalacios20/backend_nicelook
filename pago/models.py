from django.db import models
from cliente.models import Cliente
from establecimiento.models import Establecimiento
# Create your models here.

class Pago (models.Model):
    estado = models.BooleanField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)
    total = models.FloatField()
    descuento = models.FloatField(null = True)
    estado = models.BooleanField()
    fecha = models.DateField()
    metodo = models.CharField(max_length=50)
    