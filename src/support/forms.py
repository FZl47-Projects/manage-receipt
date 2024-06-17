from django import forms
from . import models


class TicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        exclude = ('is_open', 'to_user')


class TicketFormByAdminForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        exclude = ('is_open',)


class QuestionAddForm(forms.ModelForm):
    description = forms.CharField(required=False)
    image = forms.FileField(required=False)

    class Meta:
        model = models.Question
        fields = '__all__'


class AnswerSubmitForm(forms.ModelForm):
    class Meta:
        model = models.AnswerQuestion
        fields = '__all__'
