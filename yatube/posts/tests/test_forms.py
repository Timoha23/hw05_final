import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ..models import Group, Post, User, Comment

COUNT_POSTS_ADDED = 1
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='user')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

        cls.guest_client = Client()

        cls.user_not_author = User.objects.create_user(
            username='user_not_author')
        cls.authorized_user_not_author = Client()
        cls.authorized_user_not_author.force_login(cls.user_not_author)

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Форма создает запись в Post"""
        posts_count = Post.objects.count()

        new_post_text = 'Тестовый пост 2'
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

        form_data = {
            'text': new_post_text,
            'image': uploaded,
        }

        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username}))

        self.assertEqual(Post.objects.count(), posts_count + COUNT_POSTS_ADDED)

        self.assertTrue(Post.objects.filter(author=self.user,
                                            text='Тестовый пост 2',
                                            group=None,
                                            image='posts/small.gif',
                                            ).exists())

    def test_edit_post(self):
        """Тест редактирования поста с последующим его измненением в БД"""
        post_count = Post.objects.count()
        new_post_text = 'Текст поста изменен'
        post = self.post
        response = self.authorized_user.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data={'text': new_post_text},
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id}))
        self.assertEqual(new_post_text, Post.objects.get(id=post.id).text)
        self.assertTrue(Post.objects.filter(author=self.user,
                                            text=self.post.text,
                                            pub_date=self.post.pub_date,
                                            group=None).exists)
        self.assertEqual(Post.objects.count(), post_count)

    def test_not_auth_user_cant_edit(self):
        """Тестируем, что неавторизованный
        пользователь не может редактировать пост
        """
        new_post = Post.objects.create(
            author=self.user,
            text='Новый тестовый пост',
        )

        new_post_text = 'Редактируем пост'
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': new_post.id}),
            data={'text': new_post_text},
            follow=True,
        )

        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{new_post.id}/edit/')
        self.assertTrue(Post.objects.filter(author=self.user,
                                            text=new_post.text,
                                            pub_date=new_post.pub_date,
                                            group=None).exists)

    def test_not_auth_user_cant_create_post(self):
        """Тестируем, что неавторизованный
        пользователь не может создать пост
        """
        posts_count = Post.objects.count()
        new_post_text = 'Создаем пост'
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data={'text': new_post_text},
            follow=True,
        )

        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_auth_user_but_not_author_cant_change_author_post(self):
        """Тестируем, что авторизированный пользователь,
        не являющийся автором не может редактировать пост автора
        """
        new_post = Post.objects.create(
            author=self.user,
            text='Новый тестовый пост',
        )
        new_post_text = 'Редактируем пост'

        response = self.authorized_user_not_author.post(
            reverse('posts:post_edit', kwargs={'post_id': new_post.id}),
            data={'text': new_post_text},
            follow=True,
        )

        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': new_post.id}))
        self.assertTrue(Post.objects.filter(author=self.user,
                                            text=new_post.text,
                                            pub_date=new_post.pub_date,
                                            group=None).exists)

    def test_create_post_with_group(self):
        """Тестируем, что есть возможность создать пост и указать группу"""

        new_post_text = 'Новый тестовый пост'

        new_group = Group.objects.create(
            title='Новая тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

        count_posts_group = Post.objects.filter(group=new_group).count()

        form_data = {
            'text': new_post_text,
            'group': new_group.id,
        }

        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username}))
        self.assertEqual(Post.objects.filter(
            group=new_group).count(), count_posts_group + 1)

    def test_create_comments_for_not_auth_user(self):
        """Тестируем, что навторизованный
        пользователь не может оставить комментарий
        """
        comments_count = Comment.objects.count()
        new_comment = 'Текст комментария'
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': new_comment, },
            follow=True,
        )
        self.assertEqual(comments_count, Comment.objects.count())
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/')

    def test_create_comment(self):
        """Тестируем, что авторизованный пользователь
        может оставить комментарий
        """
        comment_count = Comment.objects.count()

        response = self.authorized_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': 'Тестовый комментарий'},
            follow=True,
        )

        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(author=self.user,
                                               text='Тестовый комментарий'))
