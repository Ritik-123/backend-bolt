import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_bolt.settings')

app = Celery('backend_bolt')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'trigger_log_entry': {
        'task': 'users.tasks.trigger_log_entry',
        'schedule': crontab(hour=23, minute=58),
    },
    'rotate_logs_every_day': {
        'task': 'users.tasks.move_rotated_logs',
        'schedule': crontab(hour=23, minute=59),
        # 'schedule': crontab(minute='*/2'),
    },
}

app.conf.timezone = 'Asia/Kolkata'
