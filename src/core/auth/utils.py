from django.core.exceptions import PermissionDenied


def object_access(obj, user, user_field='user'):
    user_role = user.role
    obj_user = getattr(obj, user_field)
    if obj_user != user and user_role not in ('super_user',):
        raise PermissionDenied
    return True
