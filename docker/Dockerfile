# Use the official Python runtime image
FROM python:3.13-slim

# Set environment variables
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Systempakete
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip
RUN pip install gunicorn

# Copy the Django project  and install dependencies
COPY requirements.txt  /app/

# run this command to install all dependencies
RUN pip install -r requirements.txt

# Copy the Django project to the container
COPY . /app/

# Make the entrypoint scripts executable
RUN chmod +x /app/docker/server-entrypoint.sh
RUN chmod +x /app/docker/worker-entrypoint.sh

# Django user and group
RUN addgroup --system django \
    && adduser --system --ingroup django django \
    && chown -R django:django /app

USER django

# HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
#     CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]