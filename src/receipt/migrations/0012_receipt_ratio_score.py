# Generated by Django 4.1.3 on 2023-10-05 10:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipt', '0011_buildingavailable'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='ratio_score',
            field=models.SmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(4)]),
        ),
    ]
