#!/bin/bash

# Start cron in the background
cron &

# Change to the project directory
cd /app/webscraper_project

# Start Gunicorn in the foreground, binding to Render's $PORT
gunicorn webscraper_project.wsgi:application --bind 0.0.0.0:$PORT