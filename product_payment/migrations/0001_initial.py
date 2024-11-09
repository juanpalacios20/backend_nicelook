# Generated by Django 5.1.1 on 2024-11-09 02:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("client", "0001_initial"),
        ("establisment", "0001_initial"),
        ("product", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product_payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("state", models.BooleanField()),
                ("discount", models.FloatField(null=True)),
                ("date", models.DateField()),
                ("method", models.CharField(max_length=50)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="client.client"
                    ),
                ),
                (
                    "establisment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="establisment.establisment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductPaymentDetail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.FloatField()),
                (
                    "payment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="details",
                        to="product_payment.product_payment",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="product.product",
                    ),
                ),
            ],
            options={
                "unique_together": {("product", "payment")},
            },
        ),
        migrations.AddField(
            model_name="product_payment",
            name="products",
            field=models.ManyToManyField(
                through="product_payment.ProductPaymentDetail", to="product.product"
            ),
        ),
    ]
