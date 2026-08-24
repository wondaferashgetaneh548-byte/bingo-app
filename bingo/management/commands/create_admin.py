from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        User = get_user_model()
        user, created = User.objects.get_or_create(username='admin')
        user.email = 'admin@example.com'
        user.set_password('Admin12345!')
        user.is_superuser = True
        user.is_staff = True
        user.save()
        self.stdout.write(self.style.SUCCESS('Superuser updated successfully!'))