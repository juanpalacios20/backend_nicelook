from django.contrib import admin
from .models import EmployeeServices, ServicioForm

# Register your models here.

class ServicioAdmin(admin.ModelAdmin):
    form = ServicioForm
    fields = ('duracion',)
    
    
admin.site.register(EmployeeServices)
