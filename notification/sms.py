from core.utils import send_sms, get_host_url


class NotificationUser:

    @classmethod
    def handler_custom_notification(cls, notification, phonenumber):
        pattern = 'wqdr0q1prygkpw3'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_task_rejected(cls, notification, phonenumber):
        pattern = 'p9ngl2gh2r27nwi'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_task_accepted(cls, notification, phonenumber):
        pattern = '9yv5dvz8o621fd0'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_receipt_accepted(cls, notification, phonenumber):
        pattern = 'wm3zd85p5zwv9o4'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_receipt_rejected(cls, notification, phonenumber):
        pattern = 'wkriosvfmlipo40'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_password_changed_successfully(cls, notification, phonenumber):
        pattern = 'l10y99rssw7wowy'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_reset_password_code_sent(cls, notification, phonenumber):
        pattern = 'x0lxvu9yywd4ub4'
        send_sms(phonenumber, pattern, {
            'code': notification.kwargs['code']
        })

    @classmethod
    def handler_user_account_activated(cls, notification, phonenumber):
        # TODO: should be completed
        pattern = '...'
        send_sms(phonenumber, pattern, {
            'user_name': notification.to_user.get_full_name()
        })


class Notification:

    @classmethod
    def handler_custom_notification(cls, phonenumber, instance, user):
        values = {
            'user_name': user.get_full_name(),
            'notification_url': get_host_url(instance.get_absolute_url())
        }
        pattern = 'wqdr0q1prygkpw3'
        send_sms(phonenumber, pattern, values)


NOTIFICATION_USER_HANDLERS = {
    'CUSTOM_NOTIFICATION': NotificationUser.handler_custom_notification,
    'TASK_REJECTED': NotificationUser.handler_task_rejected,
    'TASK_ACCEPTED': NotificationUser.handler_task_accepted,
    'RECEIPT_ACCEPTED': NotificationUser.handler_receipt_accepted,
    'RECEIPT_REJECTED': NotificationUser.handler_receipt_rejected,
    'PASSWORD_CHANGED_SUCCESSFULLY': NotificationUser.handler_password_changed_successfully,
    'RESET_PASSWORD_CODE_SENT': NotificationUser.handler_reset_password_code_sent,
    'USER_ACCOUNT_ACTIVATED': NotificationUser.handler_user_account_activated
}
