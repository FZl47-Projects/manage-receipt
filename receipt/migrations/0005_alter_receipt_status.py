# Generated by Django 4.1.3 on 2023-09-13 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipt', '0004_alter_receipt_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='status',
            field=models.CharField(choices=[('accepted', 'تایید شده'), ('pending', 'در صف'), ('rejected', 'رد شده')], default='pending', max_length=15),
        ),
    ]
