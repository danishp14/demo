# Generated by Django 5.1.3 on 2024-12-05 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0012_customer_discount_remaining_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='carwashservice',
            name='final_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
