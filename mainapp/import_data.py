import json
from django.core.management.base import BaseCommand
from .models import Videos  # Replace 'yourapp' with the actual name of your Django app

class Command(BaseCommand):
    help = 'Import data from JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        json_file_path = options['json_file']

        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                for video_data in data.get('videos', []):
                    Videos.objects.create(**video_data)
                self.stdout.write(self.style.SUCCESS('Data imported successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {e}'))
