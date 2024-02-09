import os
from .base import BASE_DIR

DEBUG = True
SERVE_FILE_BY_DJANGO = os.environ.get('SERVE_FILE_BY_DJANGO', True)

ALLOWED_HOSTS = ['*']
HOST_ADDRESS = 'http://127.0.0.1:8000'
CSRF_TRUSTED_ORIGINS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

REDIS_CONFIG = {
    'HOST': 'localhost',
    'PORT': '6379'
}

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

STATIC_ROOT = BASE_DIR / 'static_collected'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
