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

# Test if cron is working
echo "Testing cron setup..."
crontab -l
echo "Cron jobs listed above"

# Check if cron service is running
ps aux | grep cron

# Ejecutar scraping inicial para verificar que funciona
echo "=== Ejecutando scraping inicial ==="
python manage.py scrape
echo "=== Scraping inicial completado ==="

# Verificar si se guardaron datos
echo "=== Verificando datos guardados ==="
python manage.py shell -c "
from scraper.models import ScrapedItem
count = ScrapedItem.objects.count()
print(f'Total elementos en BD: {count}')
if count > 0:
    latest = ScrapedItem.objects.latest('created_at')
    print(f'Último elemento: {latest.title[:50]}...')
"

# Start following the cron log in background (for debugging)
tail -f /var/log/cron.log &

# Start Gunicorn in the foreground, binding to Render's $PORT
gunicorn webscraper_project.wsgi:application --bind 0.0.0.0:$PORT