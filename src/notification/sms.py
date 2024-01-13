from core.utils import send_sms, get_host_url


class NotificationUser:

    @classmethod
    def handler_custom_notification(cls, notification, phonenumber):
        pattern = 'ar0prdkncw4dk9l'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_task_rejected(cls, notification, phonenumber):
        pattern = 'l3mss27nedv0uie'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_task_accepted(cls, notification, phonenumber):
        pattern = 'eogp6f640vqyl4c'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_receipt_accepted(cls, notification, phonenumber):
        pattern = 'f66pu45gjbi1z8n'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_receipt_rejected(cls, notification, phonenumber):
        pattern = '2fmfs2d5dlkt0aj'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_password_changed_successfully(cls, notification, phonenumber):
        pattern = 'b2pw4o745dqs1hs'
        send_sms(phonenumber, pattern, {
            'notification_url': get_host_url(notification.get_link()),
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_reset_password_code_sent(cls, notification, phonenumber):
        pattern = '0pcbtnsuif87g32'
        send_sms(phonenumber, pattern, {
            'code': notification.kwargs['code']
        })

    @classmethod
    def handler_user_account_activated(cls, notification, phonenumber):
        pattern = 'teouuo7p8oy9fd7'
        send_sms(phonenumber, pattern, {
            'user_name': notification.to_user.get_full_name()
        })

    @classmethod
    def handler_confirm_phonenumber_code_sent(cls, notification, phonenumber):
        pattern = 'hx4h9y3wpxzt5gs'
        send_sms(phonenumber, pattern, {
            'code': notification.kwargs['code']
        })

    @classmethod
    def handler_phonenumber_confirmed(cls, notification, phonenumber):
        pattern = 'sk44rthuce0y29o'
        send_sms(phonenumber, pattern, {
            'user_name': notification.to_user.get_full_name()
        })


    @classmethod
    def handler_survey_notification(cls, notification, phonenumber):
        pattern = '685xfvaiep1qflg'
        send_sms(phonenumber, pattern, {
            'user_name': notification.to_user.get_full_name(),
            'question_link': notification.kwargs['question_link'],
        })


class Notification:

    @classmethod
    def handler_custom_notification(cls, phonenumber, instance, user):
        values = {
            'user_name': user.get_full_name(),
            'notification_url': get_host_url(instance.get_absolute_url())
        }
        pattern = 'bctaipldk4ywqqt'
        send_sms(phonenumber, pattern, values)


NOTIFICATION_USER_HANDLERS = {
    'CUSTOM_NOTIFICATION': NotificationUser.handler_custom_notification,
    'TASK_REJECTED': NotificationUser.handler_task_rejected,
    'TASK_ACCEPTED': NotificationUser.handler_task_accepted,
    'RECEIPT_ACCEPTED': NotificationUser.handler_receipt_accepted,
    'RECEIPT_REJECTED': NotificationUser.handler_receipt_rejected,
    'PASSWORD_CHANGED_SUCCESSFULLY': NotificationUser.handler_password_changed_successfully,
    'RESET_PASSWORD_CODE_SENT': NotificationUser.handler_reset_password_code_sent,
    'USER_ACCOUNT_ACTIVATED': NotificationUser.handler_user_account_activated,
    'CONFIRM_PHONENUMBER_CODE_SENT': NotificationUser.handler_confirm_phonenumber_code_sent,
    'PHONENUMBER_CONFIRMED': NotificationUser.handler_phonenumber_confirmed,
    'SURVEY_NOTIFICATION': NotificationUser.handler_survey_notification,
}
