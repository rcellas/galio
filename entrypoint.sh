#!/bin/bash

# Start cron in the background
cron &

# Start Gunicorn in the foreground, binding to Render's $PORT
gunicorn webscraper_project.wsgi:application --bind 0.0.0.0:$PORT