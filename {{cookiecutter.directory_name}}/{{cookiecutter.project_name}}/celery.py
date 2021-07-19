import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{cookiecutter.project_name}}.settings.development')

app = Celery(f"{{{{cookiecutter.project_name}}}}_{os.getenv('DJANGO_SETTINGS_MODULE').split('.')[-1]}")

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {

}
