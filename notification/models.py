from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from jsonfield import JSONField
from core.models import BaseModel

User = get_user_model()


def upload_notification_src(instance, path):
    frmt = str(path).split('.')[-1]
    return f'images/notifications/{get_random_string(20)}.{frmt}'


class Notification(BaseModel):
    """
        notification in site
    """
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=upload_notification_src, null=True, blank=True, max_length=400)
    send_notify = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = '-is_active', '-id'

    def __str__(self):
        return self.get_title()

    def get_title(self):
        return self.title or 'notification'

    def get_content(self):
        return f"""
            {self.get_title()}
            {self.description}
        """

    def get_absolute_url(self):
        return reverse('notification:notification_dashboard_detail',args=(self.id,))


class NotificationUser(BaseModel):
    """
        notification for user
    """
    type = models.CharField(max_length=100)
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    # attach content
    image = models.ImageField(upload_to=upload_notification_src, null=True, blank=True, max_length=400)
    kwargs = JSONField(null=True, blank=True)

    send_notify = models.BooleanField(default=True)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    # show for user or not
    is_showing = models.BooleanField(default=True)

    class Meta:
        ordering = '-id',

    def __str__(self):
        return f'notification for {self.to_user}'

    def get_title(self):
        return self.title or 'notification'

    def get_content(self):
        return f"""
            {self.get_title()}
            {self.description}
        """

    def get_absolute_url(self):
        return reverse('notification:notification_dashboard_user_detail', args=(self.id,))

    def get_link(self):
        try:
            return self.kwargs['link']
        except:
            return self.get_absolute_url()

    def get_image(self):
        try:
            return self.image.url
        except:
            return None
