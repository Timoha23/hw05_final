from django.test import TestCase

from ..models import Group, Post, Comment, User, FIRST_FIFTEEN_SYMBOLS


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, пятнадцать символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = self.post
        post_text = post.text[:FIRST_FIFTEEN_SYMBOLS]
        self.assertEqual(post_text, str(post))

    def test_model_post_verbose_name(self):
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Относится к группе...',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).verbose_name,
                                 expected_value)

    def test_help_text(self):
        post = self.post
        field_verboses = {
            'text': 'Введите основной текст поста',
            'group': 'Выберите группу, к которой относится ваш пост',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).help_text,
                                 expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_model_group_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__"""
        group = self.group
        group_title = group.title
        self.assertEqual(group_title, str(group))


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='user')

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, пятнадцать символов',
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def test_model_comment_verbose_name_and_help_text(self):
        """Тестируем verbose_name и help_text модели Comment"""
        comment = self.comment

        self.assertEqual(comment._meta.get_field('text').help_text,
                         'Введите комментарий')
        self.assertEqual(comment._meta.get_field('text').verbose_name,
                         'Текст комментария')
