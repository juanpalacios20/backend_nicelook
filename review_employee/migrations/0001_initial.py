# Generated by Django 5.1.1 on 2024-11-14 23:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('appointment', '0001_initial'),
        ('client', '0001_initial'),
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=500)),
                ('rating', models.FloatField()),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='appointment.appointment')),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.client')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employee')),
            ],
        ),
    ]
