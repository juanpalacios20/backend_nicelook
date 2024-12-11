from django.db import models
from django.contrib.auth.models import User
from establisment.models import Establisment

class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    googleid = models.CharField(null=True)
    token = models.CharField(null=True)
    accestoken = models.CharField(null=True)
    
    def __str__ (self):
        return self.user.username