
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements /code/requirements

RUN pip install --upgrade pip wheel

RUN pip install -r /code/requirements/local.txt

COPY . /code

RUN chmod +x /code/entrypoint.sh

EXPOSE 8000

ENV EATLY_ENV_ID=local
ENV DJANGO_SETTINGS_MODULE=settings.base

ENTRYPOINT ["/code/entrypoint.sh"]
