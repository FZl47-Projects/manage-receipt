# Generated by Django 4.1.3 on 2023-08-13 13:53

from django.db import migrations, models
import support.models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='degree_of_importance',
            field=models.CharField(choices=[('low', 'کم'), ('medium', 'متسوط'), ('high', 'زیاد')], default='low', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=support.models.upload_file_src),
        ),
        migrations.DeleteModel(
            name='TicketReplay',
        ),
    ]
