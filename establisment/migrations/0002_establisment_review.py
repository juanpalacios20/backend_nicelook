# Generated by Django 5.1.1 on 2024-09-26 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('establisment', '0001_initial'),
        ('review', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='establisment',
            name='review',
            field=models.ManyToManyField(to='review.review'),
        ),
    ]
