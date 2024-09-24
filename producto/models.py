from django.db import models
from establecimiento.models import Establecimiento

# Create your models here.
class Producto (models.Model):
    Establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=500)
    precio = models.FloatField()
    marca = models.CharField(max_length=50)
    distruibuidor = models.CharField(max_length=50)
    fecha_ingreso = models.DateField()
    fecha_vencimiento = models.DateField()
    cantidad = models.IntegerField()
    estado = models.BooleanField()
    descuento = models.FloatField()
    
    def __str__ (self):
        return self.nombre