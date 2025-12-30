from celery import Celery
from ..config import get_settings

settings = get_settings()

# Initialize Celery app
celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "worker.tasks.google_drive.*": {"queue": "google_drive"},
        "worker.tasks.dropbox.*": {"queue": "dropbox"},
    },
)


class TaskService:
    """Service for queuing async import tasks."""

    def queue_google_drive_import(self, job_id: str, folder_id: str) -> None:
        """Queue a Google Drive import task."""
        celery_app.send_task(
            "worker.tasks.google_drive.import_folder",
            args=[job_id, folder_id],
            queue="google_drive",
        )

    def queue_dropbox_import(self, job_id: str, shared_link: str) -> None:
        """Queue a Dropbox import task."""
        celery_app.send_task(
            "worker.tasks.dropbox.import_folder",
            args=[job_id, shared_link],
            queue="dropbox",
        )
