from django.db import models

from establisment.models import Establisment

class Schedule(models.Model):
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    
    def __str__(self):
        return f"{self.start_date} {self.end_date}"