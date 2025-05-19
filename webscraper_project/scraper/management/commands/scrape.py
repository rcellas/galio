from django.core.management.base import BaseCommand
from scraper.services.scrape import scrape_multiple_websites, urls, keywords
from scraper.models import ScrapedItem

class Command(BaseCommand):
    help = 'Ejecuta el scraping y guarda los resultados en la base de datos'

    def handle(self, *args, **kwargs):
        scraped_data = scrape_multiple_websites(urls, keywords)
        print("Scraped data:", scraped_data)
        for item in scraped_data:
            try:
                obj = ScrapedItem.objects.create(
                    url_base=item.get("url_base"),
                    title=item.get("title"),
                    link=item.get("link"),
                    pdf_url=item.get("pdf_url")
                )
                print("✅ Guardado:", obj)
            except Exception as e:
                print("❌ Error guardando:", e)
        self.stdout.write(self.style.SUCCESS('Scraping completado y datos guardados.'))