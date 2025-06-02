from django.core.management.base import BaseCommand
from scraper.services.scrape import scrape_multiple_websites, save_scraped_data, get_urls, get_keywords

class Command(BaseCommand):
    help = 'Ejecuta el scraping y guarda los resultados en la base de datos'

    def handle(self, *args, **kwargs):
        try:
            urls = get_urls()
            keywords = get_keywords()
            scraped_data = scrape_multiple_websites(urls, keywords)
            save_scraped_data(scraped_data)  
            self.stdout.write(self.style.SUCCESS('Scraping completado y datos guardados.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Error: {str(e)}'))