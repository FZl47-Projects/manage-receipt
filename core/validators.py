from django.conf import settings
from django.core.exceptions import PermissionDenied

def validator_img_format(frmt):
    allow_formats = settings.IMAGE_FORMATS
    if not (frmt in allow_formats):
        raise PermissionDenied(f'format img is not valid. format should be one of this{allow_formats.__repr__()}')
    