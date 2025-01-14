from django.db import models
from client.models import Client
from employee.models import Employee
from service.models import Service

# Create your models here.
class Appointment_Request(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    services = models.ManyToManyField(Service)
    estate = models.BooleanField(default=False)
    

    def __str__(self):
        return f"Cita solicitada por {self.client.user.first_name} para el servicio {self.services.first().name}"