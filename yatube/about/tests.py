from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLSandTemplatesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exists_at_desired_location(self):
        """Проверка корректности перехода по страницам"""
        urls_names = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for urls, status in urls_names.items():
            with self.subTest(urls=urls):
                response = self.guest_client.get(urls)
                self.assertEqual(response.status_code, status)

    def test_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_urls_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_urls_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
