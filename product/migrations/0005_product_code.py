# Generated by Django 5.1.1 on 2024-10-14 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_alter_product_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='code',
            field=models.BigIntegerField(default=0),
        ),
    ]
