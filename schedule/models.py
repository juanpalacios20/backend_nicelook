from django.db import models
from employee.models import Employee
from establisment.models import Establisment
from django.contrib.postgres.fields import ArrayField

class Time (models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    time_start_day_one = models.TimeField()
    time_end_day_one = models.TimeField()
    time_start_day_two = models.TimeField(null=True)
    time_end_day_two = models.TimeField(null=True)
    double_day = models.BooleanField()
    date_start = models.DateField()
    date_end = models.DateField()
    
    
    def __str__(self):
        return self.employee.user.username
 
class TimeException (models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField(null=True)
    reason = models.CharField(max_length=250)
    time_start = models.TimeField(null=True)
    time_end = models.TimeField(null=True)
    
    def __str__(self):
        return self.employee.user.username
     