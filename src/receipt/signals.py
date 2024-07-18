import hashlib

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
def handle_receipt(sender, instance, created, **kwargs):
    if created:
        # Calculate hash of the image using SHA-256
        image_data = instance.picture.read()
        picture_hash = hashlib.sha256(image_data).hexdigest()
        instance.picture_hash = picture_hash
        instance.save(update_fields=['picture_hash'])

    if instance.status == 'accepted':
        NotificationUser.objects.create(
            type='RECEIPT_ACCEPTED',
            to_user=instance.user,
            title=messages.RECEIPT_PERFORMED_SUCCESSFULLY.format(instance.user.get_full_name()),
            kwargs={
                'link': instance.get_absolute_url(),
                'tracking_code': instance.tracking_code
            },
        )
    elif instance.status == 'rejected':
        NotificationUser.objects.create(
            type='RECEIPT_REJECTED',
            to_user=instance.user,
            title=messages.RECEIPT_PERFORMED_FAILED.format(instance.user.get_full_name(), instance.get_absolute_url()),
            kwargs={
                'link': instance.get_absolute_url(),
                'tracking_code': instance.tracking_code
            },
        )
