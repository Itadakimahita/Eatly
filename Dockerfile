# Use official Python image
FROM python:3.11-slim

# set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working dir
WORKDIR /code

# system deps (add libs if you need, e.g. libpq-dev)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY ./requirements/local.txt /code/requirements/local.txt
RUN pip install --upgrade pip
RUN pip install -r /code/requirements/local.txt

# Copy project
COPY . /code

# Make entrypoint executable
RUN chmod +x /code/entrypoint.sh

# Expose port (gunicorn default)
EXPOSE 8000

# Default env (can be overridden)
ENV EATLY_ENV_ID=local
ENV DJANGO_SETTINGS_MODULE=your_project.settings

# Run entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]
