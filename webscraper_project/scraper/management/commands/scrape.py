from django.core.management.base import BaseCommand
from scraper.services.scrape import scrape_multiple_websites
from scraper.models import ScrapedData

class Command(BaseCommand):
    help = "Run the web scraper"

    def handle(self, *args, **kwargs):
        # Definir URLs y palabras clave
        urls = ["https://dogv.gva.es/es/inici"]
        keywords = ["subvención", "licitación", "licitació", "contratació", "contractación", "contractaciones"]

        # Ejecutar scraping
        data = scrape_multiple_websites(urls, keywords)
        print("Scraped Data:", data)  # Depuración

        # Guardar en la base de datos
        for item in data:
            ScrapedData.objects.create(
                url=item["url"],
                title=item["title"]  # Corregido de "text" a "title"
            )

        self.stdout.write(self.style.SUCCESS("Scraping completed!"))