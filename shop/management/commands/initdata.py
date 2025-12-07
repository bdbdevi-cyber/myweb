from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import call_command
import os
class Command(BaseCommand):
    help = 'Run migrations, create superuser (admin/admin123) and load demo products fixture'
    def handle(self, *args, **options):
        self.stdout.write('Running makemigrations for shop and migrate...')
        call_command('makemigrations', 'shop')
        call_command('migrate')
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            self.stdout.write('Creating superuser admin...')
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        else:
            self.stdout.write('Superuser already exists.')
        self.stdout.write('Loading product fixtures...')
        fixture = os.path.join('fixtures', 'products.json')
        call_command('loaddata', fixture)
        self.stdout.write(self.style.SUCCESS('Init data complete.'))
