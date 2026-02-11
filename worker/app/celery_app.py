from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "orchestrator_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=5,
    task_routes={
        "app.jobs.orchestration.*": {"queue": "orchestration"},
        "app.jobs.alerts.*": {"queue": "alerts"},
        "app.jobs.ai.*": {"queue": "ai"},
    },
    beat_schedule={
        "evaluate-alert-rules": {
            "task": "app.jobs.alerts.evaluate_alert_rules",
            "schedule": 60.0,
        }
    },
)

celery_app.autodiscover_tasks(["app.jobs"])
