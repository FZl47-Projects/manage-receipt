FROM hub.hamdocker.ir/library/python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SUPERUSER_PASSWORD admin

ADD ./requirements.txt /root/app/

WORKDIR /root/app
RUN pip install -r requirements.txt --timeout 1000
RUN pip install gunicorn --timeout 1000
ADD ./src /root/app/src

WORKDIR /root/app/src

CMD while ! python manage.py sqlflush > /dev/null ; do sleep 1; done && \
    python manage.py makemigrations --noinput && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py qcluster 2>&1 & \
    gunicorn --bind 0.0.0.0:8000 config.wsgi

