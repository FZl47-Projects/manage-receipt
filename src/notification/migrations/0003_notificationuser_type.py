# Generated by Django 4.1.3 on 2023-09-11 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_alter_notification_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationuser',
            name='type',
            field=models.CharField(default='test', max_length=100),
            preserve_default=False,
        ),
    ]