import string
import logging
import random
import datetime
import jdatetime
import requests
import json
import pytz
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail as _send_email_django
from django.conf import settings
from django_q.tasks import async_task
from django.contrib import messages

_logger = logging.getLogger('root')


def random_str(size=15, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def random_num(size=10, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_time(frmt='%Y-%m-%d_%H:%M'):
    tz = pytz.timezone('Asia/Tehran')
    time = datetime.datetime.now(tz)
    if not frmt:
        return time
    return time.strftime(frmt)


def get_timesince_persian(time):
    time_server = get_time(None)

    diff_time = datetime.datetime(time_server.year, time_server.month, time_server.day, time_server.hour,
                                  time_server.minute) - datetime.datetime(time.year, time.month, time.day, time.hour,
                                                                          time.minute)

    diff_time_sec = diff_time.total_seconds()
    # sec = diff_time_sec % 60
    min = int(diff_time_sec // 60 % 60)
    hour = int(diff_time_sec // 3600)
    day = diff_time.days
    result = ''
    if min > 0:
        result = f'{min} دقیقه پیش'
    else:
        result = f'لحظاتی پیش'

    if hour > 0:
        result = f'{hour} ساعت پیش'

    if day > 0:
        result = f'{day}  روز پیش'

    return result


def send_sms(phonenumber, pattern_code, values={}):
    phonenumber = str(phonenumber).replace('+', '')
    payload = json.dumps({
        "pattern_code": pattern_code,
        "originator": settings.SMS_CONFIG['ORIGINATOR'],
        "recipient": phonenumber,
        "values": values
    })
    headers = {
        'Authorization': "AccessKey {}".format(settings.SMS_CONFIG['API_KEY']),
        'Content-Type': 'application/json'
    }

    async_task(requests.request,
               'POST',
               settings.SMS_CONFIG['API_URL'],
               headers=headers,
               data=payload
               )


def send_email(email, subject, content, **kwargs):
    # send email in background
    async_task(_send_email_django,
               subject,
               content,
               settings.EMAIL_HOST_USER,
               [email]
               )


def add_prefix_phonenum(phonenumber):
    phonenumber = str(phonenumber).replace('+98', '')
    return f'+98{phonenumber}'


def get_raw_phonenum(phonenumber):
    p = str(phonenumber).replace('+98', '')
    return p


def form_validate_err(request, form):
    if form.is_valid() is False:
        errors = form.errors.as_data()
        if errors:
            for field, err in errors.items():
                err = str(err[0])
                err = err.replace('[', '').replace(']', '')
                err = err.replace("'", '').replace('This', '')
                err = f'{field} {err}'
                messages.error(request, err)
        else:
            messages.error(request, _('Incorrect Data'))
        return False
    return True


def create_form_messages(request, form):
    errors = form.errors.as_data()
    if errors:
        for field, err in errors.items():
            err = str(err[0])
            err = err.replace('[', '').replace(']', '')
            err = err.replace("'", '').replace('This', '')
            err = f'{field} {err}'
            messages.error(request, err)
    else:
        messages.error(request, _('Incorrect Data'))


def get_host_url(url):
    return settings.HOST_ADDRESS + url


def get_media_url(url):
    return settings.MEDIA_URL + url


def log_event(msg, level='info', exc_info=False, **kwargs):
    level = level.upper()
    levels = {
        'NOTSET': 0,
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50,
    }
    logging.log(levels[level], msg=msg, exc_info=exc_info, **kwargs)


def gregorian_to_jalali(year, month, day):
    g_date = jdatetime.GregorianToJalali(year, month, day)
    return f'{g_date.jyear}-{g_date.jmonth}-{g_date.jday}'
