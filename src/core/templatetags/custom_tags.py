from django import template
from django.utils.translation import gettext_lazy

register = template.Library()


@register.simple_tag
def call(obj, method_name, *args, **kwargs):
    """Call obj's method and pass it the given parameters"""

    return getattr(obj, method_name)(*args, **kwargs)


@register.simple_tag
def translate(text):
    return gettext_lazy(text)
