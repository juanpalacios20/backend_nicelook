from django.db import models
from cliente.models import Cliente

# Create your models here.

class Reseña (models.Model):
    autor = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=500)
    valoracion = models.FloatField()
    
    def __str__(self):
        return self.comentario