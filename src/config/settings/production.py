import os
import pymysql
from .base import BASE_DIR

# use pymysql driver(MYSQL)
pymysql.install_as_MySQLdb()

DEBUG = False
SERVE_FILE_BY_DJANGO = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')
ALLOWED_HOSTS.append('app')  # add docker service(app service)
HOST_ADDRESS = os.environ.get('HOST_ADDRESS').split(',')
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS').split(',')
CORS_ALLOW_ALL_ORIGINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
    }
}

Q_CLUSTER = {
    'name': 'django-q',
    'timeout': 60,
    'redis': {
        'host': 'redis',  # service docker (redis dns|name)
        'port': 6379,
        'db': 0,
        'socket_timeout': None,
        'charset': 'utf-8',
        'errors': 'strict',
    }
}
REDIS_CONFIG = {
    'HOST': 'redis',  # service docker (redis dns|name)
    'PORT': '6379'
}

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

STATIC_ROOT = BASE_DIR.parent / 'volumes/static'
MEDIA_ROOT = BASE_DIR.parent / 'volumes/media'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

