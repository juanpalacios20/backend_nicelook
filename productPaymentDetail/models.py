from django.db import models
from product.models import Product

class ProductPaymentDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    payment = models.ForeignKey('product_payment.Product_payment', on_delete=models.CASCADE, related_name='details')
    quantity = models.FloatField()

    class Meta:
        app_label = 'product_payment'
        unique_together = ('product', 'payment')
    
    def __str__(self):
        return f"{self.product} - {self.quantity} units"