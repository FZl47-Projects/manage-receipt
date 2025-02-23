# Generated by Django 3.2 on 2024-06-17 10:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('receipt', '0021_auto_20240615_0412'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='receipttask',
            options={'permissions': (('auto_accept_receipt_task', 'Accept receipt task automatically'), ('view_full_receipts_task', 'Can view all receipts task'), ('view_in_user_detail_receipt_tasks', 'Can access to receipt tasks in user detail page'), ('view_admin_receipt_task', 'Can access to receipt tasks user by admin role'), ('user_accept_receipt_task', 'User can accept receipt task'), ('user_reject_receipt_task', 'User can reject receipt task'))},
        ),
    ]
