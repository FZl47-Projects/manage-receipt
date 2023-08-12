from django import forms
from . import models


class NotificationForm(forms.ModelForm):
    class Meta:
        model = models.Notification
        exclude = ('is_active',)


class NotificationUserForm(forms.ModelForm):
    class Meta:
        model = models.NotificationUser
        exclude = ('is_showing',)
