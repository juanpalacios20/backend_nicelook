from django.db import models
from employee.models import Employee
from establisment.models import Establisment
from django.contrib.postgres.fields import ArrayField

class Schedule(models.Model):
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    
    def __str__(self):
        return f"{self.start_date} {self.end_date}"

class Time (models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    time_start_day_one = models.TimeField()
    time_end_day_one = models.TimeField()
    time_start_day_two = models.TimeField(null=True)
    time_end_day_two = models.TimeField(null=True)
    double_day = models.BooleanField()
    state = models.BooleanField()
    working_days = ArrayField(models.CharField(max_length=10), blank=True, null=True)
    
    
    def __str__(self):
        return self.employee.user.username