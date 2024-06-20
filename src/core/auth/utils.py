from django.core.exceptions import PermissionDenied
from django.contrib.auth import models as permission_models
from django.contrib.auth import get_user_model

User = get_user_model()


def get_available_permissions():
    MODELS = (
        'user', 'group',

        'receipt', 'receipttask', 'building', 'buildingavailable', 'project',

        'notification', 'notificationuser',

        'question', 'answerquestion',
    )
    return permission_models.Permission.objects.filter(content_type__model__in=MODELS)


def object_access(obj, user, user_field='user'):
    user_role = user.role
    obj_user = getattr(obj, user_field)
    if obj_user != user and user_role not in ('super_user',):
        raise PermissionDenied
    return True
