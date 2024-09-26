from django.db import models
from service.models import Service
from employee.models import Employee

# Create your models here.
class EmployeeServices (models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    commission = models.FloatField()
    
    
    def __str__ (self):
        return self.service.name
