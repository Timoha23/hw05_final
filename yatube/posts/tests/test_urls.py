from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLSandTemplatesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author')
        cls.user_not_author = User.objects.create_user(username='not_author')

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client_author = Client()

        cls.authorized_client_author.force_login(cls.user_author)
        cls.authorized_client.force_login(cls.user_not_author)

        cls.group = Group.objects.create(
            title='Текстовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

    # Тесты доступности страниц
    def test_uses_correct_urls(self):
        """Проверка корректности перехода по страницам"""
        urls_names = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.post.author}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/follow/': HTTPStatus.FOUND,
        }
        for urls, status in urls_names.items():
            with self.subTest(urls=urls):
                response = self.guest_client.get(urls)
                self.assertEqual(response.status_code, status)

    def test_posts_postid_edit_for_author(self):
        """Страница с редактированием поста автора, доступна только автору"""
        response = self.authorized_client_author.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_postid_edit_for_not_author(self):
        """Страница с редактированием поста недоступна не автору"""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/',
                                              follow=True)
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_posts_postid_edit_for_not_auth_user(self):
        """Страница с редактирование недоступна не авторизованному"""
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')

    def test_create_for_auth(self):
        """Страница с созданием поста доступна авторизированному"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_not_auth(self):
        """Страница с созданием поста недоступна не авторизованному"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_follow_for_auth(self):
        """Страница follow доступна авторизированному"""
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_for_not_auth(self):
        """Страница follow не доступна неавторизованному"""
        response = self.guest_client.get('/follow/')
        self.assertRedirects(response, '/auth/login/?next=/follow/')

    # Проверка вызываемых HTML-шаблонов
    def test_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_urls_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for address, template in templates_urls_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)


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
