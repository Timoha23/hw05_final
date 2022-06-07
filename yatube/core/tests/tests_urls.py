from django.test import TestCase, Client

from posts.models import User


class PostsPagesTests(TestCase):
    def setUp(self):
        super().setUpClass()
        self.user_1 = User.objects.create_user(username='user_1')
        self.authorized_user_1 = Client()
        self.authorized_user_1.force_login(self.user_1)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        response = self.authorized_user_1.get('/404pagenotfound/')
        self.assertTemplateUsed(response, 'core/404.html')
