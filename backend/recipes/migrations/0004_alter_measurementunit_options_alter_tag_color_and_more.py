# Generated by Django 4.1 on 2022-08-28 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_measurementunit_alter_recipe_author_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='measurementunit',
            options={'ordering': ['name'], 'verbose_name': 'Единица измерения', 'verbose_name_plural': 'Единицы измерения'},
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, unique=True, verbose_name='Цветовой HEX-код'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=30, unique=True, verbose_name='Название'),
        ),
    ]
