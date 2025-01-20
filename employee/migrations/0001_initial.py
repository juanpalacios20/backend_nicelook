# Generated by Django 5.1.1 on 2025-01-20 10:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0001_initial'),
        ('establisment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField()),
                ('phone', models.CharField(max_length=15)),
                ('state', models.BooleanField()),
                ('googleid', models.CharField(blank=True, null=True)),
                ('token', models.CharField(blank=True, null=True)),
                ('accestoken', models.CharField(blank=True, null=True)),
                ('especialty', models.ManyToManyField(to='category.category')),
                ('establisment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='establisment.establisment')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
