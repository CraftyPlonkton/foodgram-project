# Generated by Django 4.1 on 2022-09-08 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_remove_following_not_following_yourself_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='following',
            constraint=models.UniqueConstraint(fields=('subscriber', 'author'), name='unique_following'),
        ),
    ]
