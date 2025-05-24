from django.db import models
from django.core.exceptions import ValidationError


class ScrapedItem(models.Model):
    id = models.AutoField(primary_key=True)
    url_base = models.URLField()
    title = models.TextField(max_length=2000)
    link = models.URLField(null=True, blank=True)
    pdf_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if len(self.title) > 2000:
            raise ValidationError(f'El título no puede exceder los 2000 caracteres')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title