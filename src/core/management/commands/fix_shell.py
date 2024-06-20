from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'fix some data'

    def handle(self, *args, **kwargs):
        from account.models import User

        User.objects.filter(role='normal_user').update(role='common_user')
        User.objects.filter(role='financial_user').update(role='admin_user')


