from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField('e-mail адресс', unique=True, max_length=254)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    following = models.ManyToManyField(
        'self',
        through='Following',
        symmetrical=False,
        verbose_name='Подписки на авторов',
        related_name='followers',
        blank=True,
    )
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe',
        verbose_name='Список покупок',
        related_name='shopping_cart',
        blank=True
    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username


class Following(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('author')),
                name='not_following_yourself'),
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_following')
        ]

    def __str__(self):
        return f'{self.subscriber} --> {self.author}'
