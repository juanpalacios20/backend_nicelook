# Generated by Django 5.1.1 on 2024-10-17 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='total',
            field=models.BigIntegerField(default=0),
        ),
    ]