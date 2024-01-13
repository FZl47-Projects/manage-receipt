from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from notification.models import NotificationUser
from .models import Question

User = get_user_model()


@receiver(post_save, sender=Question)
def handle_notification_users_question_create(sender, instance, created, **kwargs):
    if not created:
        return
    users = instance.building.get_users()
    for user in users:
        NotificationUser.objects.create(
            type='SURVEY_NOTIFICATION',
            to_user=user,
            title='اطلاع رسانی نظرسنجی',
            description=f"""
                نظر سنجی {instance.title}
            """,
            kwargs={
                'question_link': instance.get_absolute_url()
            }
        )
