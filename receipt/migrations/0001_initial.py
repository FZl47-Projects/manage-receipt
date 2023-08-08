# Generated by Django 4.1.3 on 2023-08-08 07:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import receipt.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('address', models.TextField()),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('amount', models.PositiveBigIntegerField()),
                ('picture', models.ImageField(upload_to=receipt.models.upload_receipt_pic_src)),
                ('is_checked', models.BooleanField(default=False)),
                ('submited_at', models.DateTimeField(auto_now_add=True)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='receipt.building')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReceiptTask',
            fields=[
                ('receipt_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='receipt.receipt')),
                ('status', models.CharField(choices=[('checked', 'checked'), ('pending', 'pending'), ('rejected', 'rejected')], default='pending', max_length=15)),
                ('description_task', models.TextField(blank=True, null=True)),
                ('user_admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_admin', to=settings.AUTH_USER_MODEL)),
                ('user_super_admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_super_admin', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-id',),
                'abstract': False,
            },
            bases=('receipt.receipt', models.Model),
        ),
    ]