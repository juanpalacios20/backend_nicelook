# Generated by Django 5.1.1 on 2024-10-11 15:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('establisment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Receptionist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=15)),
                ('googleid', models.CharField(null=True)),
                ('token', models.CharField(null=True)),
                ('accestoken', models.CharField(null=True)),
                ('establisment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='establisment.establisment')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
