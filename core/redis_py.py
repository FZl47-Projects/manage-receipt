import redis
import pickle
from functools import wraps
from django.conf import settings

REDIS = None
REDIS_CONFIG = settings.REDIS_CONFIG


def create_conn():
    global REDIS
    REDIS = redis.Redis(host=REDIS_CONFIG['HOST'], port=REDIS_CONFIG['PORT'])
    return REDIS


def decorator_command(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if REDIS is None:
            create_conn()
        return func(*args, **kwargs)

    return wrapper


@decorator_command
def test_conn():
    try:
        REDIS.client()
        return True
    except Exception as e:
        pass
    return False


@decorator_command
def pack_data(data):
    return pickle.dumps(data)


@decorator_command
def unpack_data(data):
    return pickle.loads(data)


@decorator_command
def add_to_list(key, data):
    data = pack_data(data)
    REDIS.lpush(key, data)
    return True


@decorator_command
def get_list(key):
    data = REDIS.lrange(key, 0, -1)
    return data


@decorator_command
def get_list_upacked(key):
    return [unpack_data(data) for data in get_list(key)]


@decorator_command
def get_len_list(key):
    return REDIS.llen(key)


@decorator_command
def remove_first_element_list(key):
    REDIS.lrem(key, 1, REDIS.lindex(key, -1))
    return True


@decorator_command
def set_value(key, value):
    REDIS.set(key, pack_data(value))
    return True


@decorator_command
def set_value_expire(key, value, seconds):
    REDIS.set(key, pack_data(value), ex=seconds)
    return True


@decorator_command
def get_value(key):
    val = REDIS.get(key)
    if val:
        return unpack_data(val)
    return None


@decorator_command
def remove_key(key):
    REDIS.delete(key)
    return True


@decorator_command
def clear_db():
    REDIS.flushdb()
    return True
