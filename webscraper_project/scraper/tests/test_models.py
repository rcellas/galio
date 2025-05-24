from django.test import TestCase
from scraper.models import ScrapedItem
from django.core.exceptions import ValidationError
from django.utils import timezone

class ScrapedItemTest(TestCase):
    def setUp(self):
        self.item = ScrapedItem.objects.create(
            url_base="https://example.com",
            title="Test Subvención",
            link="https://example.com/doc",
            pdf_url="https://example.com/doc.pdf"
        )

    def test_scraped_item_creation(self):
        self.assertTrue(isinstance(self.item, ScrapedItem))
        self.assertEqual(self.item.title, "Test Subvención")

    def test_scraped_item_fields(self):
        self.assertEqual(self.item.url_base, "https://example.com")
        self.assertEqual(self.item.link, "https://example.com/doc")
        self.assertEqual(self.item.pdf_url, "https://example.com/doc.pdf")

    def test_string_representation(self):
        self.assertEqual(str(self.item), "Test Subvención")

    def test_invalid_url_format(self):
        with self.assertRaises(ValidationError):
            item = ScrapedItem(
                url_base="url-invalida",
                title="Test URL Inválida"
            )
            item.full_clean()

    def test_missing_required_fields(self):
        with self.assertRaises(ValidationError):
            item = ScrapedItem()
            item.full_clean()

    def test_empty_title(self):
        with self.assertRaises(ValidationError):
            item = ScrapedItem(
                url_base="https://example.com",
                title=""
            )
            item.full_clean()

    def test_invalid_pdf_url(self):
        with self.assertRaises(ValidationError):
            item = ScrapedItem(
                url_base="https://example.com",
                title="Test",
                pdf_url="no-es-url-pdf"
            )
            item.full_clean()

    def test_extremely_long_title(self):
        with self.assertRaises(ValidationError):
            item = ScrapedItem(
                url_base="https://example.com",
                title="a" * 10000 
            )
            item.full_clean()