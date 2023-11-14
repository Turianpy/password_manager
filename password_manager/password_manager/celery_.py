import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'password_manager.settings')

app = Celery('password_manager')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
