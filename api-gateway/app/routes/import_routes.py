import uuid
import re
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ImportJob
from ..schemas import ImportRequest, ImportResponse, JobStatusResponse
from ..services.task_service import TaskService

router = APIRouter(prefix="/import", tags=["Import"])


def extract_google_drive_folder_id(url: str) -> str:
    """Extract folder ID from Google Drive URL."""
    patterns = [
        r"drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/drive/u/\d+/folders/([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid Google Drive folder URL")


def extract_dropbox_shared_link(url: str) -> str:
    """Extract and validate Dropbox shared link."""
    if "dropbox.com" not in url:
        raise ValueError("Invalid Dropbox URL")
    # Convert to direct download link format if needed
    if "?dl=0" in url:
        url = url.replace("?dl=0", "?dl=1")
    elif "?dl=1" not in url:
        url = url + "?dl=1"
    return url


@router.post("/google-drive", response_model=ImportResponse)
async def import_from_google_drive(
    request: ImportRequest,
    db: Session = Depends(get_db),
):
    """
    Import images from a public Google Drive folder.

    The import process runs asynchronously. Use the returned job_id
    to track progress via GET /jobs/{job_id}.
    """
    try:
        folder_id = extract_google_drive_folder_id(request.folder_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create import job
    job_id = str(uuid.uuid4())
    job = ImportJob(
        id=job_id,
        source="google_drive",
        source_url=request.folder_url,
        status="pending",
    )
    db.add(job)
    db.commit()

    # Queue the import task
    task_service = TaskService()
    task_service.queue_google_drive_import(job_id, folder_id)

    return ImportResponse(
        job_id=job_id,
        status="processing",
        message="Import job started. Use GET /jobs/{job_id} to track progress.",
    )


@router.post("/dropbox", response_model=ImportResponse)
async def import_from_dropbox(
    request: ImportRequest,
    db: Session = Depends(get_db),
):
    """
    Import images from a public Dropbox folder.

    The import process runs asynchronously. Use the returned job_id
    to track progress via GET /jobs/{job_id}.
    """
    try:
        shared_link = extract_dropbox_shared_link(request.folder_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create import job
    job_id = str(uuid.uuid4())
    job = ImportJob(
        id=job_id,
        source="dropbox",
        source_url=request.folder_url,
        status="pending",
    )
    db.add(job)
    db.commit()

    # Queue the import task
    task_service = TaskService()
    task_service.queue_dropbox_import(job_id, shared_link)

    return ImportResponse(
        job_id=job_id,
        status="processing",
        message="Import job started. Use GET /jobs/{job_id} to track progress.",
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    """Get the status of an import job."""
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    progress_percent = 0.0
    if job.total_files > 0:
        progress_percent = round(
            (job.processed_files / job.total_files) * 100, 2
        )

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        source=job.source,
        source_url=job.source_url,
        total_files=job.total_files,
        processed_files=job.processed_files,
        failed_files=job.failed_files,
        progress_percent=progress_percent,
        error_message=job.error_message,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )
