from django.utils.translation import gettext_lazy as _

# task messages
TASK_REJECTED = _('Your request has been rejected')

TASK_ACCEPTED = _('Your request has been accepted')

RECEIPT_ACCEPTED = _('Your receipt has been accepted')

RECEIPT_REJECTED = _('Your receipt has been rejected')

RECEIPT_PERFORMED_SUCCESSFULLY = _("""
    Hello, 
    Mr/Mrs
    {} 
    Your submitted receipt has been successfully accepted.
""")

RECEIPT_PERFORMED_FAILED = _("""
    Hello, 
    Mr/Mrs
    {} 
    Your submitted receipt has been rejected.
    See the link {} for more information
""")
