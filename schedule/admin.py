from django.contrib import admin
from .models import Time
from .models import TimeException
# Register your models here.
admin.site.register(Time)
admin.site.register(TimeException)