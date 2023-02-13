import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from data/ingredients.csv'

    def handle(self, *args, **options):
        try:
            with open(f'{settings.BASE_DIR}/data/ingredients.csv',
                      'r', encoding='utf-8') as ing_file:
                reader = csv.reader(ing_file, delimiter=',')
                upload_list = []
                for row in reader:
                    name, measurement_unit = row
                    newby = Ingredient(
                            name=name,
                            measurement_unit=measurement_unit)
                    if newby not in upload_list:
                        upload_list.append(newby)
                Ingredient.objects.bulk_create(upload_list)
                self.stdout.write(
                    self.style.SUCCESS('Ингредиенты загружены успешно'))

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('Упс, что-то пошло не так...'))
            raise CommandError(
                'В директории data отсутствует файл с ингредиентами')
