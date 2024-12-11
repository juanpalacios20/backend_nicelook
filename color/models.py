from django.db import models
from establisment.models import Establisment

# Create your models here.
class Color(models.Model):
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE, default=1)
    code = models.CharField(max_length=10)
    
    def __str__(self):
        return self.code
