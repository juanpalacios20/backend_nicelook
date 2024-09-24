from django.db import models

class Agenda(models.Model):
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()
    
    def __str__(self):
        return f"{self.fecha_inicio} {self.fecha_final}"