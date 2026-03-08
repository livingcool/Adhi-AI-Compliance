from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Modules that contain Celery task definitions
TASK_MODULES = [
    "app.workers.tasks",
    "app.workers.compliance_tasks",
]

# Fallback to in-memory broker if Redis is not configured (e.g., local dev without Redis)
broker_url = settings.CELERY_BROKER_URL or "memory://"
result_backend = settings.CELERY_RESULT_BACKEND or "cache+memory://"

celery_app = Celery(
    "adhi_worker",
    broker=broker_url,
    backend=result_backend,
    include=TASK_MODULES,
)

# Import task_routes to set them properly
from app.workers.task_routes import task_routes, CPU_QUEUE, GPU_QUEUE  # noqa: E402

# Compliance queue
COMPLIANCE_QUEUE = "compliance_tasks"

_scan_interval_hours = settings.COMPLIANCE_SCAN_INTERVAL_HOURS or 24

# Build beat schedule from configured interval
_beat_schedule = {
    "periodic-compliance-scan": {
        "task": "compliance.scan_all_systems",
        "schedule": crontab(minute=0, hour=f"*/{_scan_interval_hours}"),
        "args": [],
        "kwargs": {"org_id": None},
        "options": {"queue": COMPLIANCE_QUEUE},
    },
}

celery_app.conf.update(
    # Task acknowledgement
    task_acks_late=True,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    # Serialisation
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Queues
    task_default_queue=CPU_QUEUE,
    task_routes={
        **task_routes,
        "compliance.*": {"queue": COMPLIANCE_QUEUE},
    },
    # Beat schedule
    beat_schedule=_beat_schedule,
    beat_scheduler="celery.beat:PersistentScheduler",
    # Timeouts
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
)

if __name__ == "__main__":
    celery_app.start()