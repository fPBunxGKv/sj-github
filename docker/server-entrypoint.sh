#!/bin/sh
set -e

echo "Fixing permissions..."
chown -R django:django /app/staticfiles /app/data

echo "Waiting for database..."
until python manage.py migrate
do
    echo "Database not ready, retrying..."
    sleep 2
done

echo "Collecting static files..."
su-exec django python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec su-exec django gunicorn sj.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 4