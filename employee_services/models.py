from django.db import models
from service.models import Service
from employee.models import Employee
from django import forms

# Create your models here.
class EmployeeServices (models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    duration = models.DurationField()
    

    def __str__ (self):
        return self.service.name


class ServicioForm(forms.ModelForm):
    duracion = forms.DurationField(widget=forms.TextInput(attrs={'placeholder': 'HH:MM:SS'}))

    class Meta:
        model = Service
        fields = ('duracion',)