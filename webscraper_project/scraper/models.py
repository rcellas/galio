from django.db import models

class ScrapedItem(models.Model):
    id = models.AutoField(primary_key=True)
    url_base = models.URLField()
    title = models.TextField()
    link = models.URLField(null=True, blank=True)
    pdf_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)