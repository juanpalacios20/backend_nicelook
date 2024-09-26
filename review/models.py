from django.db import models
from client.models import Client

# Create your models here.

class Review (models.Model):
    autor = models.ForeignKey(Client, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    rating = models.FloatField()
    
    def __str__(self):
        return self.comment