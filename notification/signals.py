from django.db.models.signals import post_save
from django.dispatch import receiver
from core.utils import send_email, send_sms
from .models import NotificationUser


@receiver(post_save,sender=NotificationUser)
def handle_notification_notify(sender,instance,**kwargs):
    if instance.send_notify:
        user = instance.to_user
        phone_number = user.phonenumer
        email = user.email
        if phone_number:
            send_sms(phone_number,instance.get_content())
        if email:
            send_email(email,instance.get_content())
    
    

    
    