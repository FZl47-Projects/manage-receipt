from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'It initial the things that the project needs to start'

    def handle(self, *args, **kwargs):
        from django.contrib.auth.models import Group, Permission

        user_group_default, created = Group.objects.get_or_create(name='common_user_group_default')
        if created:
            user_group_default.permissions.add(*[
                # TODO: add permissions
                # Permission.objects.get(codename='')
            ])