from django.db import models
from schedule.models import Schedule
from service.models import Service
from client.models import Client

# Create your models here.

class Appointment (models.Model):
    date = models.DateField()
    time = models.DateTimeField()
    estate = models.BooleanField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service)
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.time
    