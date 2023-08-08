from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'phonenumber')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'phonenumber')


class RegisterUserForm(forms.ModelForm):
    password2 = forms.CharField(max_length=64, min_length=8, required=True, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('phonenumber', 'password', 'password2')

    def clean_password2(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password2')
        if p1 != p2:
            raise forms.ValidationError('passwords is not same')
        return p2


