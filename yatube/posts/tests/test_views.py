from math import ceil

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, User, Comment, Follow

LIMIT_POSTS_FOR_PAGE = 10
COUNT_POSTS_FIRST_PAGE = 10
COUNT_POSTS_SECOND_PAGE = 3
POST_NUMBER_1 = 0
PAGE_NUMBER_2 = str(ceil((COUNT_POSTS_FIRST_PAGE
                          + COUNT_POSTS_SECOND_PAGE) / LIMIT_POSTS_FOR_PAGE))


class PostsPagesTests(TestCase):
    def setUp(self):
        super().setUpClass()
        self.user_1 = User.objects.create_user(username='firstuser')
        self.authorized_user_1 = Client()
        self.authorized_user_1.force_login(self.user_1)

        self.user_2 = User.objects.create_user(username='seconduser')
        self.authorized_user_2 = Client()
        self.authorized_user_2.force_login(self.user_2)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        self.group_1 = Group.objects.create(
            title='Группа 1',
            slug='slug-group-1',
            description='Тестовое описание группы 1'
        )

        self.group_2 = Group.objects.create(
            title='Группа 2',
            slug='slug-group-2',
            description='Тестовое описание группы 1'
        )

        self.first_post_user_1 = Post.objects.create(
            author=self.user_1,
            text='Первый пост юзера 1',
            image=uploaded,
            group=self.group_1,
        )

        self.comment = Comment.objects.create(
            post=self.first_post_user_1,
            author=self.user_1,
            text='Тестовый комментарий',
        )

    def test_views_correct_templates(self):
        """Проверка вью на корректность используемых шаблонов"""
        views_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                    'slug': self.group_1.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                    'username': self.user_1.username}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                    'post_id': self.first_post_user_1.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                    'post_id': self.first_post_user_1.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for view, template in views_templates_names.items():
            with self.subTest(template=template):
                response = self.authorized_user_1.get(view)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_user_1.get(reverse('posts:index'))
        first_object = response.context['page_obj'][POST_NUMBER_1]

        len_objects = len(response.context['page_obj'])
        index_author_0 = first_object.author.username
        index_text_0 = first_object.text
        index_id_0 = first_object.id
        index_image_0 = first_object.image

        self.assertEqual(len_objects, Post.objects.all().count())
        self.assertEqual(index_author_0,
                         self.first_post_user_1.author.username)
        self.assertEqual(index_text_0, self.first_post_user_1.text)
        self.assertEqual(index_id_0, self.first_post_user_1.id)
        # image in context
        self.assertEqual(index_image_0, self.first_post_user_1.image)

    def test_group_posts_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом"""
        response_1 = self.authorized_user_1.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_1.slug}))

        len_response_1 = len(response_1.context['page_obj'])
        first_object = response_1.context['page_obj'][POST_NUMBER_1]
        group_posts_author_0 = first_object.author.username
        group_posts_text_0 = first_object.text
        group_posts_id_0 = first_object.id
        group_posts_image_0 = first_object.image

        group_object = response_1.context['group']

        self.assertEqual(len_response_1,
                         Post.objects.filter(group=self.group_1).count())
        self.assertEqual(group_posts_author_0,
                         self.first_post_user_1.author.username)
        self.assertEqual(group_posts_text_0, self.first_post_user_1.text)
        self.assertEqual(group_posts_id_0, self.first_post_user_1.id)
        self.assertEqual(group_posts_image_0, self.first_post_user_1.image)

        self.assertEqual(group_object, self.group_1)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_user_1.get(reverse(
            'posts:profile', kwargs={'username': self.user_1.username}))

        len_objects = len(response.context['page_obj'])
        first_object = response.context['page_obj'][POST_NUMBER_1]
        profile_author_0 = first_object.author.username
        profile_text_0 = first_object.text
        profile_id_0 = first_object.id
        profile_image_0 = first_object.image

        author_object = response.context['author']

        self.assertEqual(len_objects, Post.objects.filter(
            author=self.user_1).count())
        self.assertEqual(profile_author_0,
                         self.first_post_user_1.author.username)
        self.assertEqual(profile_text_0, self.first_post_user_1.text)
        self.assertEqual(profile_id_0, self.first_post_user_1.id)
        self.assertEqual(author_object, self.user_1)
        self.assertEqual(profile_image_0, self.first_post_user_1.image)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_user_1.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.first_post_user_1.id})
        )
        post_object = response.context['post']

        post_detail_author = post_object.author.username
        post_detail_text = post_object.text
        post_detail_id = post_object.id
        post_detail_image = post_object.image

        self.assertEqual(post_detail_author,
                         self.first_post_user_1.author.username)
        self.assertEqual(post_detail_text, self.first_post_user_1.text)
        self.assertEqual(post_detail_id, self.first_post_user_1.id)
        self.assertEqual(post_detail_image, self.first_post_user_1.image)

    def test_post_edit_correct_context(self):
        """Шаблон create_post для вью post_edit
         сформирован с правильным контекстом
         """
        response = self.authorized_user_1.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.first_post_user_1.id}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertEqual(response.context['post_id'],
                         self.first_post_user_1.id)
        self.assertTrue(response.context['post_edit'])

    def test_create_post_correct_context(self):
        """Шаблон create_post для вью post_create
        сформирован с правильным контекстом"""
        response = self.authorized_user_1.get(reverse(
            'posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = User.objects.create_user(username='author')
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.user_author)

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )

        for i in range(COUNT_POSTS_FIRST_PAGE + COUNT_POSTS_SECOND_PAGE):
            cls.post = Post.objects.create(
                author=cls.user_author,
                text='Тестовый пост №' + str(i),
                group=cls.group,
            )

    def test_paginator_for_index_for_first_page(self):
        """Проверка корректности работы пагинатора для первой страницы index"""
        response = self.authorized_client_author.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                         COUNT_POSTS_FIRST_PAGE)

    def test_paginator_for_index_for_second_page(self):
        """Проверка корректности работы пагинатора для второй страницы index"""
        response = self.authorized_client_author.get(f'/?page={PAGE_NUMBER_2}')
        self.assertEqual(len(response.context['page_obj']),
                         COUNT_POSTS_SECOND_PAGE)

    def test_paginator_for_group_list_first_page(self):
        """Проверка корректности работы пагинатора
         для первой страницы group_list
        """
        response = self.authorized_client_author.get(
            f'/group/{self.group.slug}/')
        self.assertEqual(len(response.context['page_obj']),
                         COUNT_POSTS_FIRST_PAGE)

    def test_paginator_for_group_list_second_page(self):
        """Проверка корректности работы пагинатора
        для второй страницы group_list
        """
        response = self.authorized_client_author.get(
            f'/group/{self.group.slug}/?page={PAGE_NUMBER_2}')
        self.assertEqual(len(response.context['page_obj']),
                         COUNT_POSTS_SECOND_PAGE)

    def test_paginator_for_profile_for_first_page(self):
        """Проверка корректности работы пагинатора
        для первой страницы profile
        """
        response = self.authorized_client_author.get(
            f'/profile/{self.post.author.username}/')
        self.assertEqual(len(response.context['page_obj']),
                         COUNT_POSTS_FIRST_PAGE)

    def test_paginator_for_profile_for_second_page(self):
        """Проверка корректности работы
        пагинатора для второй страницы profile
        """
        response = self.authorized_client_author.get(
            f'/profile/{self.post.author.username}/?page={PAGE_NUMBER_2}')
        self.assertEqual(len(response.context['page_obj']),
                         COUNT_POSTS_SECOND_PAGE)


class CachesTest(TestCase):
    def setUp(self):
        super().setUpClass()
        self.user_1 = User.objects.create_user(username='user_1')
        self.authorized_user_1 = Client()
        self.authorized_user_1.force_login(self.user_1)

        self.post = Post.objects.create(
            author=self.user_1,
            text='Тест',
        )

    def test_caches_index(self):
        """Тестируем кеширование на главной странице"""
        response = self.authorized_user_1.get(reverse('posts:index'))
        Post.objects.filter(pk=self.post.pk).delete()
        response_2 = self.authorized_user_1.get(reverse('posts:index'))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_2 = self.authorized_user_1.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_2.content)


class FollowingTest(TestCase):
    def setUp(self):
        super().setUpClass()
        # follower
        self.user_1 = User.objects.create_user(username='user_1')
        self.authorized_user_1 = Client()
        self.authorized_user_1.force_login(self.user_1)
        # author
        self.user_2 = User.objects.create_user(username='user_2')
        self.authorized_user_2 = Client()
        self.authorized_user_2.force_login(self.user_2)
        # not follower
        self.user_3 = User.objects.create_user(username='user_3')
        self.authorized_user_3 = Client()
        self.authorized_user_3.force_login(self.user_3)

    def test_auth_user_can_following(self):
        """Тестируем, что авторизованный пользователь может
        подписываться на других пользователей и удалять их из подписок
        """
        self.authorized_user_1.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user_2.username}))
        self.assertTrue(Follow.objects.filter(user=self.user_1,
                                              author=self.user_2).exists())

        self.authorized_user_1.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_2.username}))
        self.assertFalse(Follow.objects.filter(user=self.user_1,
                                               author=self.user_2).exists())

    def test_new_post_add_for_followers(self):
        """Тестируем, что новый пост появляется только у подписчика"""
        self.authorized_user_1.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user_2.username}))
        post = Post.objects.create(
            author=self.user_2,
            text='Тестовый пост',
        )

        response_f = self.authorized_user_1.get(reverse('posts:follow_index'))
        first_object_f = response_f.context['page_obj'][POST_NUMBER_1]
        len_objects = len(response_f.context['page_obj'])
        first_object_f_author = first_object_f.author.username
        first_object_f_text = first_object_f.text
        first_object_f_pub_date = first_object_f.pub_date
        first_object_f_group = first_object_f.group

        self.assertEqual(len_objects, Post.objects.filter(
            author=self.user_2).count())
        self.assertEqual(first_object_f_author, post.author.username)
        self.assertEqual(first_object_f_text, post.text)
        self.assertEqual(first_object_f_pub_date, post.pub_date)
        self.assertEqual(first_object_f_group, post.group)

        response_unf = self.authorized_user_2.get(reverse(
            'posts:follow_index'))
        len_objects_unf = len(response_unf.context['page_obj'])

        self.assertNotEqual(len_objects_unf, Post.objects.filter(
            author=self.user_2).count())
