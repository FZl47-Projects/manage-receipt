from core.utils import send_email, send_sms


def handler_task_rejected(notification, phonenumber):
    pattern = 'p9ngl2gh2r27nwi'
    send_sms(phonenumber, pattern, {
        'notification_url': notification.get_absolute_url(),
    })


def handler_task_accepted(notification, phonenumber):
    pattern = '9yv5dvz8o621fd0'
    send_sms(phonenumber, pattern, {
        'notification_url': notification.get_absolute_url(),
    })


def handler_receipt_accepted(notification, phonenumber):
    pattern = '9yv5dvz8o621fd0'
    send_sms(phonenumber, pattern, {
        'notification_url': notification.get_absolute_url(),
        'user_name': notification.to_user.get_full_name()
    })


PATTERN_HANDLERS = {
    'TASK_REJECTED': handler_task_rejected,
    'TASK_ACCEPTED': handler_task_accepted,
    'RECEIPT_ACCEPTED': handler_receipt_accepted,
}
