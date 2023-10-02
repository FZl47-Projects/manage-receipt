from .base import BASE_DIR

DEBUG = True

ALLOWED_HOSTS = ['*']
HOST_ADDRESS = 'http://127.0.0.1:8000'
CSRF_TRUSTED_ORIGINS = []


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

# STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
