from django.db import models
from establisment.models import Establisment
from employee.models import Employee

# Create your models here.

class EmployeeImage(models.Model):
    establishment_id = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='images')
    image = models.BinaryField()
    
    
    def __str__(self):
        return self.employee_id.user.username
    
