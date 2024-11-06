from django.db import models
from client.models import Client
from establisment.models import Establisment
from product.models import Product

# Create your models here.

class Product_payment (models.Model):
    state = models.BooleanField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    establisment = models.ForeignKey(Establisment, on_delete=models.CASCADE)
    discount = models.FloatField(null = True)
    date = models.DateField()
    method = models.CharField(max_length=50)
    products = models.ManyToManyField(Product, through='product_payment.ProductPaymentDetail')

    class Meta:
        app_label = 'product_payment'

    def __str__ (self):
        return self.client.user.username 
    
    def total(self):
        total = 0
        for detail in self.details.all():
            total += detail.product.price * detail.quantity
        return total
    
    @property
    def total_price(self):
        total = 0
        for detail in self.details.all():
            total += detail.product.price * detail.quantity
        return total
    
    @property
    def total_quantity(self):
        total = 0
        for detail in self.details.all():
            total += detail.quantity
        return total