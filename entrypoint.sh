#!/usr/bin/env bash
set -e

echo "Environment: $EATLY_ENV_ID"

if [ "$EATLY_ENV_ID" = "prod" ] || [ "$EATLY_ENV_ID" = "production" ]; then
    echo "Installing production requirements..."
    pip install -r /code/requirements/prod.txt
else
    echo "Installing local requirements..."
    pip install -r /code/requirements/local.txt
fi

if [ -f "/code/.env" ]; then
  export $(cat /code/.env | sed 's/#.*//g' | xargs)
fi

if [ "$EATLY_ENV_ID" = "prod" ]; then
  echo "Waiting for Postgres..."
  until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
    sleep 1
  done
  echo "Postgres is ready!"
fi

python manage.py migrate --noinput

python manage.py collectstatic --noinput

# Start Django
if [ "$EATLY_ENV_ID" = "local" ]; then
  python manage.py runserver 0.0.0.0:8000
else
  gunicorn settings.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi
