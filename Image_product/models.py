from django.db import models

# Create your models here.
class ImageProduct(models.Model):
    id_establisment = models.ForeignKey('establisment.Establisment', on_delete=models.CASCADE)
    id_product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    image = models.BinaryField()