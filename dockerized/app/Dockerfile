FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SUPERUSER_PASSWORD admin

RUN apt update -y && \
    apt install gcc -y # install gcc for uwsgi lib

ADD ./requirements.txt /root/app/
ADD ./uwsgi.ini /root/app/
ADD ./run.sh /root/app/
RUN chmod 777 /root/app/run.sh

WORKDIR /root/app
RUN pip install -r requirements.txt --timeout 1000

RUN mkdir logs
WORKDIR /root/app/src

CMD while ! python manage.py sqlflush > /dev/null ; do sleep 1; done && \
    python manage.py makemigrations --noinput && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    /bin/sh -c /root/app/run.sh

