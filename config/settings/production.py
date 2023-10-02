from .base import BASE_DIR

DEBUG = False

ALLOWED_HOSTS = ['manage-receipt', 'farhikhteganmes.ir']
HOST_ADDRESS = 'https://farhikhteganmes.ir'
CSRF_TRUSTED_ORIGINS = [
    "https://www.farhikhteganmes.ir",
    "https://farhikhteganmes.ir",
    "http://farhikhteganmes.ir",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_ALL_ORIGINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'manage_receipt_db',
        'USER': 'manage_receipt_user',
        'PASSWORD': 'manage_receipt_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

# STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
