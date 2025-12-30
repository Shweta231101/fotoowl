from celery import Celery
from .config import get_settings

settings = get_settings()

# Initialize Celery app
celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.google_drive",
        "app.tasks.dropbox",
    ],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Rate limiting
    task_annotations={
        "app.tasks.google_drive.*": {"rate_limit": "10/s"},
        "app.tasks.dropbox.*": {"rate_limit": "10/s"},
    },
    # Queues
    task_queues={
        "google_drive": {"exchange": "google_drive", "routing_key": "google_drive"},
        "dropbox": {"exchange": "dropbox", "routing_key": "dropbox"},
    },
    task_default_queue="google_drive",
)

# Make app accessible for imports
app = celery_app
