from django.core.validators import MinValueValidator, MaxValueValidator
from django import forms
from . import models


class ProjectAddForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = '__all__'


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = '__all__'


class BuildingAddForm(forms.ModelForm):
    class Meta:
        model = models.Building
        exclude = ('is_active', 'progress_percentage')


class BuildingUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Building
        fields = '__all__'


class ReceiptTaskAddForm(forms.ModelForm):
    status = forms.CharField(max_length=10, required=False)

    class Meta:
        model = models.ReceiptTask
        exclude = ('user_supervisor', 'description_task')


class ReceiptAddForm(forms.ModelForm):
    ratio_score = forms.FloatField(validators=[MinValueValidator(0), MaxValueValidator(4)], required=False)

    class Meta:
        model = models.Receipt
        exclude = ('tracking_code',)


class ReceiptAcceptForm(forms.ModelForm):
    class Meta:
        model = models.Receipt
        fields = ('amount', 'note', 'status', 'ratio_score', 'deposit_datetime')


class ReceiptRejectForm(forms.ModelForm):
    class Meta:
        model = models.Receipt
        fields = ('note', 'status')


class ReceiptUpdateForm(forms.ModelForm):
    status = forms.CharField(max_length=12, required=False)

    class Meta:
        model = models.Receipt
        fields = (
            'building', 'status', 'note', 'amount', 'ratio_score', 'deposit_datetime', 'depositor_name', 'bank_name',
            'picture')


class ReceiptTaskUpdateForm(forms.ModelForm):
    class Meta:
        model = models.ReceiptTask
        fields = ('status', 'receipt_status')
