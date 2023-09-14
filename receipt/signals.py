from django.db.models.signals import post_save
from django.dispatch import receiver
from receipt.models import ReceiptTask, Receipt
from notification.models import NotificationUser
from notification import messages


@receiver(post_save, sender=ReceiptTask)
def handle_receipt_task(sender, instance, **kwargs):
    if instance.status == 'accepted':
        instance.perform_checked()
    elif instance.status == 'rejected':
        instance.perform_rejected()


@receiver(post_save, sender=Receipt)
def handle_receipt(sender, instance, **kwargs):
    if instance.status == 'accepted':
        NotificationUser.objects.create(
            type='RECEIPT_ACCEPTED',
            to_user=instance.user,
            title=messages.RECEIPT_ACCEPTED,
            kwargs={
                'link': instance.get_absolute_url()
            },
            description="""
                            فیش شما تایید شد
            """
        )
    elif instance.status == 'rejected':
        NotificationUser.objects.create(
            type='RECEIPT_REJECTED',
            to_user=instance.user,
            title=messages.RECEIPT_REJECTED,
            kwargs={
                'link': instance.get_absolute_url()
            },
            description="""
                                    فیش شما رد شد
                    """
        )
