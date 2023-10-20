# Generated by Django 4.1.3 on 2023-09-13 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipt', '0002_alter_receipttask_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipttask',
            name='receipt_status',
            field=models.CharField(choices=[('accepted', 'تایید شده'), ('rejected', 'رد شده')], default='accepted', max_length=15),
        ),
    ]
