#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
uwsgi --ini conf/uwsgi.ini
