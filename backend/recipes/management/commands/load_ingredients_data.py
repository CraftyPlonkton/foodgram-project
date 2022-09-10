import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает в базу ингредиенты из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'path', default='../data/ingredients.csv', nargs='?',
            help='Путь до файла с данными относительно manage.py')

    def handle(self, *args, **options):
        print(options['path'])
        with open(options['path'], 'r') as file:
            reader = csv.reader(file)
            count = 1
            for row in reader:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
                print(f'Row: {count} Ingredient: {row[0]} Created: {created}')
