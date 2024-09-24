from django.db import models
from django.contrib.auth.models import User
from establecimiento.models import Establecimiento

class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)
    Establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)
    
    def __str__ (self):
        return self.user.username