#!/usr/bin/env bash

python manage.py migrate --noinput
gunicorn -b 0.0.0.0:8000 ddh_auth.wsgi:application
