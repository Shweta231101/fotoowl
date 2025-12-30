import uuid
import re
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ImportJob, Image
from ..schemas import ImportRequest, ImportResponse, JobStatusResponse
from ..services.drive_service import GoogleDriveService
from ..services.supabase_storage import SupabaseStorageService

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


def process_google_drive_import(
    job_id: str,
    folder_id: str,
    db: Session
) -> dict:
    """
    Process Google Drive import synchronously.
    Downloads images and uploads to Supabase Storage.
    """
    drive_service = GoogleDriveService()
    storage_service = SupabaseStorageService()

    try:
        # Get list of files from Google Drive folder
        files = drive_service.get_all_files_in_folder(folder_id)

        # Update job with total files
        job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
        job.total_files = len(files)
        job.status = "processing"
        db.commit()

        processed = 0
        failed = 0

        for file_info in files:
            try:
                # Download file from Google Drive
                file_content = drive_service.download_file(file_info["id"])

                # Upload to Supabase Storage
                storage_result = storage_service.upload_file(
                    file_content=file_content,
                    file_name=file_info["name"],
                    mime_type=file_info["mimeType"],
                    folder=job_id,  # Use job_id as folder for organization
                )

                # Create image record in database
                image = Image(
                    name=file_info["name"],
                    google_drive_id=file_info["id"],
                    source="google_drive",
                    size=int(file_info.get("size", 0)),
                    mime_type=file_info["mimeType"],
                    storage_path=storage_result["storage_path"],
                    storage_url=storage_result["storage_url"],
                    import_job_id=job_id,
                    status="completed",
                )
                db.add(image)
                processed += 1

            except Exception as e:
                print(f"Failed to process file {file_info['name']}: {e}")
                failed += 1

            # Update job progress
            job.processed_files = processed
            job.failed_files = failed
            db.commit()

        # Mark job as completed
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()

        return {
            "total": len(files),
            "processed": processed,
            "failed": failed,
        }

    except Exception as e:
        # Mark job as failed
        job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        raise e

    finally:
        drive_service.close()


@router.post("/google-drive", response_model=ImportResponse)
async def import_from_google_drive(
    request: ImportRequest,
    db: Session = Depends(get_db),
):
    """
    Import images from a public Google Drive folder.

    This processes the import synchronously and returns when complete.
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

    try:
        # Process import synchronously
        result = process_google_drive_import(job_id, folder_id, db)

        return ImportResponse(
            job_id=job_id,
            status="completed",
            message=f"Import completed. Processed {result['processed']} of {result['total']} images.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Import failed: {str(e)}"
        )


@router.post("/dropbox", response_model=ImportResponse)
async def import_from_dropbox(
    request: ImportRequest,
    db: Session = Depends(get_db),
):
    """
    Import images from a public Dropbox folder.

    Note: Dropbox import is not yet implemented in synchronous mode.
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

    # For now, mark as failed since Dropbox sync is not implemented
    job.status = "failed"
    job.error_message = "Dropbox synchronous import not yet implemented"
    db.commit()

    raise HTTPException(
        status_code=501,
        detail="Dropbox import is not yet available in synchronous mode"
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
