#!/bin/bash

# Start cron in the background
cron &

# Change to the project directory
cd /app/webscraper_project

# Create cron log file with proper permissions
touch /var/log/cron.log
chmod 666 /var/log/cron.log

# Run Django migrations to create database tables
python manage.py makemigrations
python manage.py migrate

# Test if cron is working (opcional - para debug)
echo "Testing cron setup..."
crontab -l

# Start Gunicorn in the foreground, binding to Render's $PORT
gunicorn webscraper_project.wsgi:application --bind 0.0.0.0:$PORT