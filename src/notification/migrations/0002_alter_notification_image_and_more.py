# Generated by Django 4.1.3 on 2023-08-13 21:49

from django.db import migrations, models
import notification.models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='image',
            field=models.ImageField(blank=True, max_length=400, null=True, upload_to=notification.models.upload_notification_src),
        ),
        migrations.AlterField(
            model_name='notificationuser',
            name='image',
            field=models.ImageField(blank=True, max_length=400, null=True, upload_to=notification.models.upload_notification_src),
        ),
    ]