from django import forms
from . import models


class TicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        exclude = ('is_open','to_user')


class TicketFormByAdminForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        exclude = ('is_open',)
