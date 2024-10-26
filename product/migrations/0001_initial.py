# Generated by Django 5.1.1 on 2024-10-25 01:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('establisment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=500)),
                ('price', models.FloatField()),
                ('brand', models.CharField(max_length=50)),
                ('distributor', models.CharField(max_length=50)),
                ('entry_date', models.DateField()),
                ('expiration_date', models.DateField()),
                ('quantity', models.IntegerField()),
                ('estate', models.BooleanField()),
                ('discount', models.FloatField()),
                ('purchase_price', models.FloatField()),
                ('code', models.BigIntegerField(default=0)),
                ('establisment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='establisment.establisment')),
            ],
        ),
    ]
