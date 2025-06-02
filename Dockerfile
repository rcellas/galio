# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.11
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

USER root
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    chromium \
    chromium-driver \
    cron \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run /var/log && \
    chmod 0755 /var/run /var/log && \
    touch /var/run/crond.pid && \
    chmod 0644 /var/run/crond.pid && \
    touch /var/log/cron.log && \
    chmod 0644 /var/log/cron.log

COPY cronfile /etc/cron.d/scrape-cron
RUN chmod 0644 /etc/cron.d/scrape-cron
RUN crontab /etc/cron.d/scrape-cron

COPY requirements.txt /app/
RUN python -m pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/webscraper_project && \
    touch /app/webscraper_project/db.sqlite3 && \
    chmod -R 777 /app/webscraper_project && \
    chmod -R 777 /app

COPY . .
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
CMD ["/app/entrypoint.sh"]