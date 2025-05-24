from django.test import TestCase
from unittest.mock import patch, MagicMock
from scraper.services.scrape import scrape_multiple_websites

class ScrapingTest(TestCase):
    def setUp(self):
        self.mock_data = [{
            "url_base": "https://example.com",
            "title": "Test Subvención",
            "link": "https://example.com/doc",
            "pdf_url": "https://example.com/doc.pdf"
        }]

    @patch('selenium.webdriver.Firefox')
    @patch('scraper.services.scrape.get_dogv_url')
    @patch('scraper.services.scrape.get_boe_url')
    @patch('scraper.services.scrape.get_bopa_url')
    @patch('scraper.services.scrape.get_dogc_url')
    def test_scrape_multiple_websites(self, mock_dogc, mock_bopa, mock_boe, mock_dogv, mock_driver):
        # Configurar mocks
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance
        
        # Mock URLs
        mock_dogv.return_value = "https://mock-dogv.com"
        mock_boe.return_value = "https://mock-boe.com"
        mock_bopa.return_value = "https://mock-bopa.com"
        mock_dogc.return_value = "https://mock-dogc.com"

        urls = ["https://example.com"]
        keywords = ["subvención"]
        results = scrape_multiple_websites(urls, keywords)
        
        self.assertIsInstance(results, list)
        mock_driver.assert_called_once()