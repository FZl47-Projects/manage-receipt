"""
    using Django 4.1.3
"""

import os
from dotenv import load_dotenv

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
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
    'public'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
                'custom_tags': 'public.templatetags.custom_tags'
            }
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "fa-ir"

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = False

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email
EMAIL_SUBJECT = 'اعلان از طرف سامانه انصاری - {} '
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

AUTH_USER_MODEL = 'account.User'  # custom normal_user model
LOGIN_URL = '/u/login-register'

COMMON_ADMIN_USER_ROLES = [
    'financial_user'
]

SUPER_ADMIN_ROLES = [
    'super_user'
]

ADMIN_USER_ROLES = [
    *COMMON_ADMIN_USER_ROLES,
    *SUPER_ADMIN_ROLES
]

USER_ROLES = [
    *ADMIN_USER_ROLES,
    'normal_user',
]

IMAGE_FORMATS = [
    'jpg',
    'png'
]

Q_CLUSTER = {
    'name': 'django-q',
    'timeout': 60,
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'socket_timeout': None,
        'charset': 'utf-8',
        'errors': 'strict',
    }
}

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

REDIS_CONFIG = {
    'HOST': 'localhost',
    'PORT': '6379'
}

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
