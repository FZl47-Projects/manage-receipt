# Generated by Django 3.2 on 2024-06-12 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_user_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, default='No name', max_length=150, verbose_name='first name'),
        ),
    ]
