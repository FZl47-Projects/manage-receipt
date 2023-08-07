from django.db import models
from core.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(BaseModel):
    """
        notification in site
    """
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    attach = models.ManyToManyField('core.File')
    send_notify = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class NotificationUser(Notification):
    """
        notification for user
    """
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'notification for {self.to_user}'
