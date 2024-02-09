#!/bin/sh

nohup python manage.py qcluster > ../logs/qcluster.log 2>&1 &
uwsgi --ini ../uwsgi.ini
