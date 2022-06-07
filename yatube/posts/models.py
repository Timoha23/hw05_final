from django.db import models
from django.contrib.auth import get_user_model


FIRST_FIFTEEN_SYMBOLS = 15
User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(unique=True, max_length=20,
                            verbose_name='Уникальный адрес группы')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите основной текст поста',)
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        related_name='posts',
        on_delete=models.SET_NULL,
        verbose_name='Относится к группе...',
        help_text='Выберите группу, к которой относится ваш пост',
    )
    image = models.ImageField(upload_to='posts/',
                              blank=True,
                              verbose_name='Картинка')

    def __str__(self):
        return self.text[:FIRST_FIFTEEN_SYMBOLS]

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = "Публикации"
        verbose_name = 'публикацию'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите комментарий',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария',
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
    )

    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
