from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from django_q.tasks import async_task
from core.utils import send_email
from .models import NotificationUser, Notification
from . import sms

User = get_user_model()


def handler_sms_notify(notification, phonenumber):
    handler_pattern = sms.NOTIFICATION_USER_HANDLERS.get(notification.type, None)
    if not handler_pattern:
        return
    handler_pattern(notification, phonenumber)


@receiver(post_save, sender=NotificationUser)
def handle_notification_user_notify(sender, instance, **kwargs):
    if instance.send_notify:
        user = instance.to_user
        phonenumber = user.phonenumber
        email = user.email
        if phonenumber:
            handler_sms_notify(instance, phonenumber)
        if email:
            subject = settings.EMAIL_SUBJECT.format(instance.title)
            send_email(email, subject, instance.get_content())


def handler_notification_notify(instance):
    users = User.normal_user.all()
    for user in users:
        phonenumber = user.phonenumber
        email = user.email
        if phonenumber:
            sms.Notification.handler_custom_notification(phonenumber,instance,user)
        if email:
            subject = settings.EMAIL_SUBJECT.format(instance.title)
            send_email(email, subject, instance.get_content())


@receiver(post_save, sender=Notification)
def handle_notification_notify(sender, instance, created, **kwargs):
    if created and instance.send_notify:
        async_task(handler_notification_notify, instance)
