# Generated by Django 4.1.3 on 2023-08-22 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipt', '0003_building_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='progress_percentage',
            field=models.IntegerField(default=0),
        ),
    ]
