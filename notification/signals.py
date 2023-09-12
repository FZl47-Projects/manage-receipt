from django.db.models.signals import post_save
from django.dispatch import receiver
from core.utils import send_email
from .models import NotificationUser, Notification
from . import sms


def handler_sms_notify(notification, phonenumber):
    handler_pattern = sms.PATTERN_HANDLERS.get(notification.type, None)
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
            send_email(email, instance.get_content())


@receiver(post_save, sender=Notification)
def handle_notification_notify(sender, instance, **kwargs):
    # TODO: should be complete
    pass
