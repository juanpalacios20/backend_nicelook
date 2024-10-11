from django.db import models
from django.contrib.auth.models import User
from schedule.models import Schedule
from category.models import Category
# Create your models here.
class Employee (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.IntegerField()
    phone = models.CharField(max_length=15)
    state = models.BooleanField()
    especialty = models.ManyToManyField(Category)
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    googleid = models.CharField(null=True)
    token = models.CharField(null=True)
    accestoken = models.CharField(null=True)
    
    
    def __str__ (self):
        return self.user.username