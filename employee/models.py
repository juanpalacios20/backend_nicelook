from django.db import models
from django.contrib.auth.models import User
from schedule.models import Schedule
from review.models import Review

# Create your models here.
class Employee (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.IntegerField()
    phone = models.CharField(max_length=15)
    estate = models.BooleanField()
    especialty = models.CharField(max_length=100)
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    googleid = models.CharField(null=True)
    token = models.CharField(null=True)
    accestoken = models.CharField(null=True)
    review = models.ManyToManyField(Review)
    
    
    def __str__ (self):
        return self.user.username