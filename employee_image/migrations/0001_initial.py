# Generated by Django 5.1.1 on 2025-01-20 10:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employee', '0001_initial'),
        ('establisment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.BinaryField()),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='employee.employee')),
                ('establishment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='establisment.establisment')),
            ],
        ),
    ]
