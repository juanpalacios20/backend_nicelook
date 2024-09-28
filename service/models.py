from datetime import timedelta
from django.db import models
from establisment.models import Establisment

# Create your models here.

class Service (models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    duracion = models.DurationField(default=timedelta(hours=1))
    category = models.CharField(max_length=100)
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    
    def __str__ (self):
        return self.name
    