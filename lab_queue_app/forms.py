from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label=_('Имя пользователя'),
        min_length=4,
        max_length=30,
        help_text=_('Допустимые символы: буквы (кириллица/латиница), цифры и подчёркивание.'),
        error_messages={
            'unique': _('Это имя уже занято.'),
            'invalid': _('Недопустимые символы.')
        }
    )
    
    email = forms.EmailField(
        label=_('Электронная почта'),
        error_messages={
            'invalid': _('Некорректный формат email.'),
            'unique': _('Этот email уже зарегистрирован.')
        }
    )
    
    password1 = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput,
        help_text=_('Минимум 8 символов, должны быть цифры и буквы.')
    )
    
    password2 = forms.CharField(
        label=_('Подтвердите пароль'),
        widget=forms.PasswordInput
    )
    
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'captcha')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9_]+$', username):
            raise ValidationError(_('Можно использовать только буквы, цифры и подчёркивание.'))
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValidationError(_('Некорректный формат email.'))
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError(_('Пароль должен быть не короче 8 символов.'))
        if not re.search(r'\d', password) or not re.search(r'[A-Za-z]', password):
            raise ValidationError(_('Пароль должен содержать буквы и цифры.'))
        return password

class ResendCaptchaForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label=_('Электронная почта'),
        error_messages={
            'invalid': _('Некорректный формат email.')
        }
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValidationError(_('Некорректный формат email.'))
        return email

class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(
        label=_('Новый пароль'),
        widget=forms.PasswordInput,
        help_text=_('Минимум 8 символов, должны быть заглавные и строчные буквы, цифры и специальные символы.')
    )
    password2 = forms.CharField(
        label=_('Подтвердите пароль'),
        widget=forms.PasswordInput
    )

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        errors = []
        if len(password) < 8:
            errors.append(_('Пароль должен быть не короче 8 символов.'))
        if not re.search(r'[A-Z]', password):
            errors.append(_('Пароль должен содержать хотя бы одну заглавную букву.'))
        if not re.search(r'[a-z]', password):
            errors.append(_('Пароль должен содержать хотя бы одну строчную букву.'))
        if not re.search(r'\d', password):
            errors.append(_('Пароль должен содержать хотя бы одну цифру.'))
        if not re.search(r'[!@#$%^&*]', password):
            errors.append(_('Пароль должен содержать хотя бы один специальный символ (!@#$%^&*).'))
        if errors:
            raise ValidationError(errors)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(_('Пароли не совпадают.'))
        return cleaned_data

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'}),
        label='Имя пользователя'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
        label='Пароль'
    )