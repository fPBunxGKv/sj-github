#!/bin/sh

echo "Waiting for database..."
until python manage.py migrate
do
    echo "Database not ready, retrying..."
    sleep 2
done

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
gunicorn sj.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 4