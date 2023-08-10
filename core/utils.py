import string
import random
from django.utils import timezone
from django.core.mail import send_mail as _send_email_django
from django.conf import settings
from django_q.tasks import async_task
from django.contrib import messages


def random_str(size=15, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_time(frmt='%Y-%m-%d_%H:%M'):
    t = timezone.now()
    if frmt is not None:
        t = t.strftime(frmt)
    return t


def send_sms(phonenumber, content, **kwargs):
    def handle(phonenumber, content, **kwargs):
        pass

    # async_task(handle)


def send_email(email, content, **kwargs):
    # send email in background 
    async_task(_send_email_django,
               settings.EMAIL_SUBJECT,
               content,
               settings.EMAIL_HOST_USER,
               [email]
               )


def add_prefix_phonenum(phonenumber):
    return f'+98{phonenumber}'


def form_validate_err(request, form):
    if form.is_valid() is False:
        errors = form.errors.as_data()
        if errors:
            errors = list(errors.values())
            err = str(errors[0][0])
            err = err.replace('[', '').replace(']', '')
            err = err.replace("'", '')
            messages.error(request, err)
        else:
            messages.error(request, 'دیتای ورودی نامعتبر است')
        return False
    return True
