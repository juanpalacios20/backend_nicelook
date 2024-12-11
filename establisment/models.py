from django.db import models

class Establisment(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=150)
    contact_methods = models.JSONField(max_length=150, null=True)
    def __str__(self):
        return self.name
