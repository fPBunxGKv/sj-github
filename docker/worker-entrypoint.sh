#!/bin/sh


# run a worker :)
celery -A sj worker --loglevel=info --concurrency 1 -E