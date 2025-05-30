# Generated by Django 4.2.21 on 2025-05-18 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScrapedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('keyword', models.CharField(max_length=100)),
                ('text', models.TextField()),
                ('link', models.URLField(blank=True, null=True)),
                ('pdf_url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='ScrapedData',
        ),
    ]
