from django.db import models
from django.contrib.auth.models import User
from establisment.models import Establisment
from schedule.models import Schedule
from category.models import Category
# Create your models here.
class Employee (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    code = models.CharField()
    phone = models.CharField(max_length=15)
    state = models.BooleanField()
    especialty = models.ManyToManyField(Category)
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, blank=True, null=True)
    googleid = models.CharField(null=True, blank=True)
    token = models.CharField(null=True, blank=True)
    accestoken = models.CharField(null=True, blank=True)
    
    
    def __str__ (self):
        return self.user.username