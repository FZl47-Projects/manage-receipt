# Generated by Django 4.1.3 on 2023-09-14 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0004_alter_notificationuser_send_notify'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationuser',
            name='link',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]