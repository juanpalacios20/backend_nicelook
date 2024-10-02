from django.db import models
from service.models import Service
from review.models import Review

class Establisment(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(error_messages=150)
    contact_methods = models.CharField(max_length=50)
    services =  models.ManyToManyField(Service, null=True)
    review = models.ManyToManyField(Review, null=True)
    def __str__(self):
        return self.name
