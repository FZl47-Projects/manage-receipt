from abc import abstractmethod

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskAdmin(models.Model):
    STATUS_OPTIONS = (
        ('accepted', _('Accepted')),
        ('pending', _('Need to check by supervisor')),
        ('rejected', _('Rejected'))
    )

    user_admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_admin')
    # superuser should be accepted or reject admins task
    user_supervisor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='user_supervisor')
    # when status changed to checked then perform function is called
    status = models.CharField(max_length=15, choices=STATUS_OPTIONS, default='pending')
    description_task = models.TextField(null=True, blank=True)

    class Meta:
        ordering = '-id',
        abstract = True

    def __str__(self):
        return f'#{self.id} task admin'

    @abstractmethod
    def perform_checked(self):
        # must implement by subclasses
        raise NotImplementedError

    @abstractmethod
    def perform_rejected(self):
        # must implement by subclasses
        raise NotImplementedError
