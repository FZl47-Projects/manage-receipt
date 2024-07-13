from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'fix some data'

    def handle(self, *args, **kwargs):
        from django.contrib.auth.models import Group
        from account.models import User

        User.objects.filter(role='normal_user').update(role='common_user')
        User.objects.filter(role='financial_user').update(role='admin_user')

        common_users = User.objects.filter(role='common_user')
        try:
            common_user_group = Group.objects.get(name='common_user_group_default')
            for user in common_users:
                user.groups.add(common_user_group)
        except Group.DoesNotExist:
            pass

        admin_users = User.objects.filter(role='admin_user')
        try:
            common_user_group = Group.objects.get(name='common_admin_group_default')
            for user in admin_users:
                user.groups.add(common_user_group)
        except Group.DoesNotExist:
            pass
