from django.db import models
from establisment.models import Establisment

class Image(models.Model):
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE, related_name='imagenes', default=1)
    image = models.BinaryField()
    description = models.CharField(max_length=255, blank=True, null=True)
    code = models.IntegerField()
    category = models.CharField(max_length=50, null=True)
    type = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"Imagen de {self.Establisment.name}"
