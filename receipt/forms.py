from django import forms
from . import models


class BuildingAddForm(forms.ModelForm):
    class Meta:
        model = models.Building
        exclude = ('is_active', 'progress_percentage')


class BuildingEditForm(forms.ModelForm):
    class Meta:
        model = models.Building
        fields = '__all__'


class ReceiptTaskAddForm(forms.ModelForm):
    class Meta:
        model = models.ReceiptTask
        exclude = ('user_super_admin', 'status', 'description_task')


class ReceiptAddForm(forms.ModelForm):
    class Meta:
        model = models.Receipt
        fields = '__all__'


class ReceiptAcceptForm(forms.ModelForm):
    class Meta:
        model = models.Receipt
        fields = ('amount', 'note', 'status')


class ReceiptRejectForm(forms.ModelForm):
    class Meta:
        model = models.Receipt
        fields = ('note', 'status')
