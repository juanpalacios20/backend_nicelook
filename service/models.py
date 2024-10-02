from datetime import timedelta
from django.db import models
from establisment.models import Establisment

from establisment.models import Establisment
from category.models import Category
# Create your models here.

class Service (models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    commission = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    state = models.BooleanField()

    
    def __str__ (self):
        return self.name
    