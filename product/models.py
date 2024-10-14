from django.db import models
from establisment.models import Establisment
from review.models import Review

# Create your models here.
class Product (models.Model):
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    price = models.FloatField()
    brand = models.CharField(max_length=50)
    distributor = models.CharField(max_length=50)
    entry_date = models.DateField()
    expiration_date = models.DateField()
    quantity = models.IntegerField()
    estate = models.BooleanField()
    discount = models.FloatField()
    review = models.ManyToManyField(Review, null=True)
    code = models.BigIntegerField(default=0)
    
    
    def __str__ (self):
        return self.name