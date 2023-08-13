from django import forms
from . import models

class TicketForm(forms.ModelForm):
    
    class Meta:
        model = models.Ticket
        exclude = ('is_open',)

        