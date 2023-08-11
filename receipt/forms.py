from django import forms
from . import models


class BuildingForm(forms.ModelForm):
    class Meta:
        model = models.Building
        fields = '__all__'
