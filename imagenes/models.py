from django.db import models
from establecimiento.models import Establecimiento  # Importar el modelo de la otra app

class ImagenEstablecimiento(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='imagenes', default=1)
    imagen = models.BinaryField()  # Aquí se almacenan las imágenes como binarios grandes
    descripcion = models.CharField(max_length=255, blank=True, null=True)  # Opcional

    def __str__(self):
        return f"Imagen de {self.establecimiento.nombre}"
