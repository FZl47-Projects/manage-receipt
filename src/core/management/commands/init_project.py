from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'It initial the things that the project needs to start'

    def handle(self, *args, **kwargs):
        from django.contrib.auth.models import Group, Permission

        user_group_default, created = Group.objects.get_or_create(name='common_user_group_default')
        if created:
            user_group_default.permissions.add(*[
                Permission.objects.get(codename='change_self_user'),
                Permission.objects.get(codename='view_building'),
                Permission.objects.get(codename='view_user_building'),
                Permission.objects.get(codename='view_project'),
                Permission.objects.get(codename='view_receipt'),
                Permission.objects.get(codename='add_receipt'),
                Permission.objects.get(codename='view_user_receipts'),
                Permission.objects.get(codename='view_question'),
                Permission.objects.get(codename='add_answerquestion'),
                Permission.objects.get(codename='view_answerquestion'),
            ])

        admin_common_group_default, created = Group.objects.get_or_create(name='common_admin_group_default')
        if created:
            admin_common_group_default.permissions.add(*[
                Permission.objects.get(codename='change_self_user'),
                Permission.objects.get(codename='add_user'),
                Permission.objects.get(codename='change_user'),
                Permission.objects.get(codename='view_user'),
                Permission.objects.get(codename='view_building'),
                Permission.objects.get(codename='view_admin_building'),
                Permission.objects.get(codename='view_financial_building'),
                Permission.objects.get(codename='view_receipts_building'),
                Permission.objects.get(codename='view_users_building'),
                Permission.objects.get(codename='view_users_score_building'),
                Permission.objects.get(codename='view_project'),
                Permission.objects.get(codename='view_receipt'),
                Permission.objects.get(codename='add_receipt'),
                Permission.objects.get(codename='change_receipt'),
                Permission.objects.get(codename='view_admin_receipts'),
                Permission.objects.get(codename='view_receipttask'),
                Permission.objects.get(codename='add_receipttask'),
                Permission.objects.get(codename='change_receipttask'),
                Permission.objects.get(codename='view_admin_receipt_task'),
                Permission.objects.get(codename='view_question'),
                Permission.objects.get(codename='view_answerquestion'),
            ])

