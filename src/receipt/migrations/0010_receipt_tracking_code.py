# Generated by Django 4.1.3 on 2023-09-26 16:35

from django.db import migrations, models
import receipt.models


class Migration(migrations.Migration):

    dependencies = [
        ('receipt', '0009_receipt_bank_name_receipt_deposit_datetime_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='tracking_code',
            field=models.CharField(default=receipt.models.random_str, max_length=10),
        ),
    ]
