# Generated by Django 4.1 on 2022-09-05 22:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_user_favorite_recipes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='followers', through='users.Following', to=settings.AUTH_USER_MODEL, verbose_name='Подписки на авторов'),
        ),
    ]
