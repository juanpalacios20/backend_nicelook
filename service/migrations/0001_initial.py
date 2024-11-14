# Generated by Django 5.1.1 on 2024-11-13 19:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('establisment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.FloatField()),
                ('image', models.BinaryField(blank=True, null=True)),
                ('commission', models.FloatField()),
                ('category', models.CharField(max_length=100)),
                ('state', models.BooleanField()),
                ('establisment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='establisment.establisment')),
            ],
        ),
    ]
