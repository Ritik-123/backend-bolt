from django.core.management.base import BaseCommand
from django.conf import settings
import os



class Command(BaseCommand):
    """
    Command to create a log directory if it doesn't exist.
    """
    
    def handle(self, *args, **kwargs):
        """
        Handle the command to create a log directory.
        """
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        arch_dir = os.path.join(settings.BASE_DIR, 'archive')
        print(log_dir)
        print(arch_dir)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            self.stdout.write(self.style.SUCCESS(f'Log directory created at {log_dir}'))
        else:
            self.stdout.write(self.style.WARNING('Log directory already exists'))
        if not os.path.exists(arch_dir):
            os.makedirs(arch_dir)
            self.stdout.write(self.style.SUCCESS(f'Archive directory created at {arch_dir}'))
        else:
            self.stdout.write(self.style.WARNING('Archive directory already exists'))