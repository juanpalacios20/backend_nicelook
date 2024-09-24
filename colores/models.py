from django.db import models
from establecimiento.models import Establecimiento 

# Create your models here.
class Colores(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, default=1)
    codigo = models.CharField(max_length=10)
    
    def __str__(self):
        return self.codigo
