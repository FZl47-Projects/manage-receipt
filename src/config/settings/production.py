import pymysql
from .base import BASE_DIR

# use pymysql driver(MYSQL)
pymysql.install_as_MySQLdb()


DEBUG = True

ALLOWED_HOSTS = ['manage-receipt', 'farhikhteganmes.ir','127.0.0.1']
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

STATIC_ROOT = '/var/www/html/manage_receipt/static'
MEDIA_ROOT = '/var/www/html/manage_receipt/media'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
