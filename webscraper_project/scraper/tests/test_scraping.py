from django.test import TestCase
from unittest.mock import patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from scraper.services.scrape import scrape_multiple_websites

class ScrapingTest(TestCase):
    def setUp(self):
        self.mock_html_bopdipu = """
        <dl>
            <dt>Resolución de subvención</dt>
            <dd>
                <span class="pdfResultadoBopa">
                    <a href="https://bopdipu.es/doc.pdf">PDF de la disposición</a>
                </span>
            </dd>
        </dl>
        """
        self.urls = ["https://bopdipu.es"]
        self.keywords = ["subvención"]

    @patch('selenium.webdriver.Firefox')
    @patch('selenium.webdriver.firefox.options.Options')
    def test_scrape_bopdipu(self, mock_options, mock_firefox):
        # Mock del driver
        mock_driver = MagicMock()
        
        # Mock de elementos DOM
        mock_dl = MagicMock()
        mock_dt = MagicMock()
        mock_dd = MagicMock()
        mock_span = MagicMock()
        mock_link = MagicMock()
        
        # Configurar comportamiento
        mock_dt.text = "Resolución de subvención"
        mock_link.get_attribute.return_value = "https://bopdipu.es/doc.pdf"
        mock_span.find_elements.return_value = [mock_link]
        mock_dd.find_elements.return_value = [mock_span]
        mock_dl.find_element.return_value = mock_dt
        
        # Configurar búsqueda de elementos
        mock_driver.find_elements.return_value = [mock_dl]
        mock_firefox.return_value = mock_driver
        
        results = scrape_multiple_websites(self.urls, self.keywords)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Resolución de subvención")