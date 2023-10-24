import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
            CSV_FILE_PATH, 'r', encoding='UTF-8'
        ) as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
        self.stdout.write(
            self.style.SUCCESS('Успешно')
        )