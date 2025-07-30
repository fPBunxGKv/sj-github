#!/bin/sh

until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done

echo "Collecting static files..."
python manage.py collectstatic --noinput

# gunicorn celery_django.wsgi --bind 0.0.0.0:8000 --workers 4 --threads 4
# exec gunicorn --bind 0.0.0.0:8000 --workers 3 sj.wsgi:application
echo "Starting Gunicorn..."
gunicorn sj.wsgi --bind 0.0.0.0:8000 --workers 4 --threads 4

# for debug
#python manage.py runserver 0.0.0.0:8000