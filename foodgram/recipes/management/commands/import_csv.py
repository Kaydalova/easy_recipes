import csv
import os

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from data/ingredients.csv'

    def handle(self, *args, **options):
        #Загружаем ингредиенты
        path = os.path.join(BASE_DIR, '/home/alexandra/Dev/foodgram-project-react/data', 'ingredients.csv')
        with open(path, encoding='utf-8') as ing_file:
            reader = csv.reader(ing_file, delimiter=',')
            upload_list = []
            for row in reader:
                upload_list.append(
                    Ingredient(
                        name=row[0],
                        measurement_unit=row[1]))
            Ingredient.objects.bulk_create(upload_list)
            print('Ингредиенты загружены успешно')
