# Generated by Django 4.1 on 2022-08-30 19:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='following',
            name='follower',
        ),
        migrations.RemoveField(
            model_name='following',
            name='following',
        ),
        migrations.AddField(
            model_name='following',
            name='author',
            field=models.ForeignKey(default=123, on_delete=django.db.models.deletion.CASCADE, related_name='authors', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='following',
            name='subscriber',
            field=models.ForeignKey(default=123, on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='followers', through='users.Following', to=settings.AUTH_USER_MODEL),
        ),
    ]
