from django.db import models
from django.contrib.auth.models import User
from establecimiento.models import Establecimiento
# Create your models here.

class Recepcionista (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    establecimiento = models.OneToOneField(Establecimiento, on_delete=models.CASCADE)
    telefono = models.CharField(15)
    
    def __str__ (self):
        return self.user.username