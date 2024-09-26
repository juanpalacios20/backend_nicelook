from django.db import models

class Schedule(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return f"{self.start_date} {self.end_date}"