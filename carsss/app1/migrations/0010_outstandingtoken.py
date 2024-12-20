# Generated by Django 5.1.3 on 2024-12-01 13:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0009_alter_carwashservice_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutstandingToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(blank=True, max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outstanding_tokens', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
