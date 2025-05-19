from django.core.management.base import BaseCommand
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.conf import settings
from users.models import User
import os

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        """
        Handle the command to create a superuser.
        """
        email= os.getenv('ADMIN_EMAIL')
        username= os.getenv('ADMIN_USERNAME')
        password= os.getenv('ADMIN_PASSWORD')

        if User.objects.filter(is_staff=True).exists():
            return "SuperAdmin already exists"
        User.objects.create_superuser(email=email, username=username, password=password)
        return "SuperAdmin created successfully"
            # self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        # except ValidationError as e:
        #     self.stderr.write(self.style.ERROR(f'Error creating superuser: {e}'))
