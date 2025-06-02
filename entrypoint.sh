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

# Check if cron service is running
ps aux | grep cron



# Start following the cron log in background (for debugging)
# tail -f /var/log/cron.log &

# Start Gunicorn in the foreground, binding to Render's $PORT
gunicorn webscraper_project.wsgi:application --bind 0.0.0.0:$PORT