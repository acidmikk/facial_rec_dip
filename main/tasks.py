from celery import shared_task
from django.utils import timezone
from main.models import Event
from scripts.prepare_data import prepare_data


@shared_task
def run_prepare_data_task(event_id):
    prepare_data(event_id)


@shared_task
def schedule_prepare_data_tasks():
    now = timezone.now()
    start_time_window = now + timezone.timedelta(hours=2)
    end_time_window = start_time_window + timezone.timedelta(minutes=30)

    events = Event.objects.filter(time_start__gte=start_time_window, time_start__lt=end_time_window)

    for event in events:
        run_prepare_data_task.apply_async(args=[event.id], eta=start_time_window)
