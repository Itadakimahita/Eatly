#!/usr/bin/env bash
set -e

if [ -f "/code/.env" ]; then
  export $(cat /code/.env | sed 's/#.*//g' | xargs)
fi

wait_for_postgres() {
  ATTEMPTS=20
  until python - <<PYCODE
import os, sys, time
import psycopg2
try:
    cfg = {
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST", "db"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
    }
    conn = psycopg2.connect(**cfg)
    conn.close()
    print("postgres ok")
    sys.exit(0)
except Exception as e:
    print("waiting for postgres...", str(e))
    sys.exit(1)
PYCODE
do
  ATTEMPTS=$((ATTEMPTS-1))
  if [ $ATTEMPTS -le 0 ]; then
    echo "Postgres did not become available, exiting"
    exit 1
  fi
  sleep 2
done
}

if [ "$EATLY_ENV_ID" = "prod" ] || [ "$EATLY_ENV_ID" = "production" ]; then
  echo "Running in production mode, waiting for Postgres..."
  wait_for_postgres
fi

echo "Apply database migrations..."
python manage.py migrate --noinput

echo "Collect static files..."
python manage.py collectstatic --noinput

if [ "$EATLY_ENV_ID" = "local" ] || [ "$EATLY_ENV_ID" = "dev" ]; then
  echo "Starting Django development server..."
  python manage.py runserver 0.0.0.0:8000
else
  echo "Starting Gunicorn..."
  gunicorn your_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi
