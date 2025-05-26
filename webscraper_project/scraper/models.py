from django.db import models

class ScrapedItem(models.Model):
    REGION_CHOICES = [
        ('Nacional', 'Nacional'),
        ('Madrid', 'Comunidad de Madrid'),
        ('Asturias', 'Asturias'),
        ('Cataluña', 'Cataluña'),
        ('Valencia', 'Comunidad Valenciana'),
    ]

    ORGANISM_CHOICES = [
        ('BOE', 'BOE'),
        ('BOCM', 'BOCM'),
        ('BOPA', 'BOPA'),
        ('BOPDIBA', 'BOPDIBA'),
        ('DOGC', 'DOGC'),
        ('DOGV', 'DOGV'),
    ]

    id = models.AutoField(primary_key=True)
    url_base = models.URLField()
    title = models.TextField()
    link = models.URLField(null=True, blank=True)
    pdf_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    region = models.CharField(max_length=50, choices=REGION_CHOICES, default='Nacional')
    organism = models.CharField(max_length=50, choices=ORGANISM_CHOICES, default='BOE')