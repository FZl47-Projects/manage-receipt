"""
    using Django 4.2
"""

import os
from dotenv import load_dotenv
from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'django_render_partial',
    'phonenumber_field',
    'django_q',
    # Apps
    'core',
    'account',
    'receipt',
    'support',
    'notification',
    'public',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'custom_tags': 'core.templatetags.custom_tags'
            }
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGES = [
    ("fa", _("Persian")),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
    BASE_DIR / 'locale/django_q',
]

LANGUAGE_CODE = "fa-ir"

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = False

USE_L10N = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email
EMAIL_SUBJECT = _('Notification from farhikhtegan mes company {}')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

AUTH_USER_MODEL = 'account.User'  # custom user model
LOGIN_URL = '/u/login-register'

IMAGE_FORMATS = [
    'jpg',
    'png'
]

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

RESET_PASSWORD_CONFIG = {
    'TIMEOUT': 300,  # by sec
    'CODE_LENGTH': 6,
    'STORE_BY': 'reset_password_phonenumber_{}'
}

CONFIRM_PHONENUMBER_CONFIG = {
    'TIMEOUT': 300,  # by sec
    'CODE_LENGTH': 6,
    'STORE_BY': 'confirm_phonenumber_{}'
}

SMS_CONFIG = {
    'API_KEY': os.environ.get('SMS_API_KEY'),
    'API_URL': 'http://rest.ippanel.com/v1/messages/patterns/send',
    'ORIGINATOR': '983000505'
}

EXPORT_ROOT_DIR = 'exports'
