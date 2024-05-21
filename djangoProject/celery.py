from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')

app = Celery('my_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'schedule-prepare-data-tasks-every-hour': {
        'task': 'my_app.tasks.schedule_prepare_data_tasks',
        'schedule': crontab(hour='*/1'),  # Запуск каждые 30 минут
    },
}
