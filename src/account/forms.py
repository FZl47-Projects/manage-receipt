from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import models as permission_models
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from receipt.models import BuildingAvailable
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'phonenumber')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'phonenumber')


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        error_messages = {
            'email': {
                'invalid': _('Email is invalid'),
                'unique': _('This email is currently in use by another user')
            }
        }


class RegisterUserForm(forms.Form):
    email_error_messages = {
        'invalid': _('Email is invalid'),
        'unique': _('This email is currently in use by another user')
    }

    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    phonenumber = PhoneNumberField(region='IR')
    email = forms.EmailField(required=True, error_messages=email_error_messages)
    password = forms.CharField(max_length=64, min_length=8, required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=64, min_length=8, required=True, widget=forms.PasswordInput())

    def clean_password2(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password2')
        if p1 != p2:
            raise forms.ValidationError('passwords is not same')
        return p2


class RegisterUserFullForm(forms.ModelForm):
    email_error_messages = {
        'invalid': _('Email is invalid'),
        'unique': _('This email is currently in use by another user')
    }
    email = forms.EmailField(required=True, error_messages=email_error_messages)
    password2 = forms.CharField(max_length=64, min_length=8, required=True, widget=forms.PasswordInput())

    class Meta:
        model = User
        exclude = ('date_joined',)
        error_messages = {
            'phonenumber': {
                'invalid': _('Phonenumber is invalid'),
                'unique': _('User with this number is already registered')
            },
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password2')
        if p1 != p2:
            raise forms.ValidationError(_('Passwords are not the same'))
        return p2


class ResetPasswordSetForm(forms.Form):
    phonenumber = PhoneNumberField(region='IR')
    code = forms.CharField()
    password = forms.CharField(max_length=64, min_length=8, required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=64, min_length=8, required=True, widget=forms.PasswordInput())

    def clean_password2(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password2')
        if p1 != p2:
            raise forms.ValidationError(_('Passwords are not the same'))
        return p2


class UserUpdateByAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('is_active', 'is_phonenumber_confirmed', 'phonenumber', 'first_name', 'last_name')


class UpdateUserPasswordForm(forms.Form):
    current_password = forms.CharField(max_length=64, min_length=8, required=True, widget=forms.PasswordInput())
    new_password = forms.CharField(max_length=64, min_length=8, required=True, widget=forms.PasswordInput())
    new_password2 = forms.CharField(max_length=64, min_length=8, required=True, widget=forms.PasswordInput())

    def clean_new_password2(self):
        p1 = self.cleaned_data.get('new_password')
        p2 = self.cleaned_data.get('new_password2')
        if p1 != p2:
            raise forms.ValidationError(_('Passwords are not the same'))
        return p2


class SetBuildingAvailableForm(forms.ModelForm):
    class Meta:
        model = BuildingAvailable
        fields = '__all__'


class PermissionGroupCreateForm(forms.ModelForm):
    class Meta:
        model = permission_models.Group
        fields = '__all__'


class PermissionGroupUpdateForm(PermissionGroupCreateForm):
    pass


class UserPermissionGroupSetForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('groups',)
