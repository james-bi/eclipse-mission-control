from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates the default scouts user'

    def handle(self, *args, **options):
        if not User.objects.filter(username='scouts').exists():
            user = User.objects.create_user(
                username='scouts',
                password='scouts',
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS('Successfully created user "scouts" with password "scouts"'))
        else:
            self.stdout.write(self.style.WARNING('User "scouts" already exists'))
