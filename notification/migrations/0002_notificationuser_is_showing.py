# Generated by Django 4.1.3 on 2023-08-10 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationuser',
            name='is_showing',
            field=models.BooleanField(default=True),
        ),
    ]