import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{cookiecutter.project_name}}.settings.development')

project = "{{cookiecutter.project_name}}"
app = Celery(f"{project}_{os.getenv('DJANGO_SETTINGS_MODULE').split('.')[-1]}")

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {

}
