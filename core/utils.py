import string
import random
from django.utils import timezone


def random_str(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_time(frmt='%Y-%m-%d_%H:%M'):
    t = timezone.now()
    if frmt is not None:
        t = t.strftime(frmt)
    return t


def send_sms(phonenumber,content,**kwargs):
    pass


def send_email(email,content,**kwargs):
    pass