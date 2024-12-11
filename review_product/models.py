from django.db import models
from client.models import Client
from product.models import Product

# Create your models here.

class ReviewProduct (models.Model):
    autor = models.ForeignKey(Client, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    rating = models.FloatField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.comment