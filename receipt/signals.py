from django.db.models.signals import post_save
from django.dispatch import receiver
from receipt.models import ReceiptTask


@receiver(post_save,sender=ReceiptTask)
def handle_receipt_task(sender,instance,**kwargs):
    if instance.status == 'checked':
        instance.perform_checked()
    elif instance.status == 'rejected':
        instance.perform_rejected()
    

    
        
            