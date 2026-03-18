from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init

from core.settings import SETTINGS
from core.observability import setup_observability

celery_app = Celery(
    "pos",
    broker=SETTINGS.celery_broker_url,
    backend=SETTINGS.celery_backend_url
)

celery_app.conf.update(
    timezone="America/Bogota",
    enable_utc=True,
    result_expires=3600,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=30,
    task_max_retries=3,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

# rutas de colas
celery_app.conf.task_routes = {
    "generate_invoice": {"queue": "invoices"},
    "low_stock_alerts": {"queue": "cron"},
    "expired_alerts": {"queue": "cron"},
}

# schedule
celery_app.conf.beat_schedule = {
    "low-stock-daily": {
        "task": "low_stock_alerts",
        "schedule": crontab(hour=SETTINGS.cron_hour_low_stock_alerts, minute=0),
    },
    "expired-daily": {
        "task": "expired_alerts",
        "schedule": crontab(hour=SETTINGS.cron_hour_expired_alerts, minute=0),
    }
}

celery_app.autodiscover_tasks(["tasks"])

@worker_process_init.connect
def init_worker(**kwargs):
    setup_observability(service_name='worker')
