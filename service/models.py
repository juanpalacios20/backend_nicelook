from datetime import timedelta
from django.db import models
from establisment.models import Establisment
from category.models import Category
# Create your models here.

class Service (models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    commission = models.FloatField()
    category = models.CharField(max_length=100)
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    state = models.BooleanField()

    
    def __str__ (self):
        return self.name

class ImageService (models.Model):
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    image = models.BinaryField()
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__ (self):
        return self.service