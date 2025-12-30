from celery import shared_task, group
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Dict, Any
import logging

from ..config import get_settings
from ..services.dropbox_service import DropboxService
from ..services.supabase_storage import SupabaseStorageService

settings = get_settings()
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="worker.tasks.dropbox.import_folder",
)
def import_folder(self, job_id: str, shared_link: str):
    """
    Import all images from a Dropbox shared folder.

    This task:
    1. Lists all images in the folder
    2. Updates job with total count
    3. Spawns individual tasks for each image
    """
    logger.info(f"Starting Dropbox import for job {job_id}")

    db = get_db()

    try:
        # Get Dropbox service
        dropbox_service = DropboxService()

        # List all files in folder
        files = dropbox_service.list_shared_folder_files(shared_link)
        total_files = len(files)

        logger.info(f"Found {total_files} images in folder")

        # Update job with total count
        db.execute(
            """
            UPDATE import_jobs
            SET total_files = :total, status = 'processing'
            WHERE id = :job_id
            """,
            {"total": total_files, "job_id": job_id},
        )
        db.commit()

        if total_files == 0:
            # No files to import
            db.execute(
                """
                UPDATE import_jobs
                SET status = 'completed', completed_at = :now
                WHERE id = :job_id
                """,
                {"job_id": job_id, "now": datetime.utcnow()},
            )
            db.commit()
            return {"status": "completed", "total": 0}

        # Process files in chunks
        chunk_size = settings.chunk_size
        for i in range(0, total_files, chunk_size):
            chunk = files[i : i + chunk_size]

            # Create group of tasks for this chunk
            tasks = group(
                process_single_file.s(job_id, shared_link, file_info)
                for file_info in chunk
            )
            tasks.apply_async()

        return {"status": "processing", "total": total_files}

    except Exception as e:
        logger.error(f"Error in import_folder: {str(e)}")
        db.execute(
            """
            UPDATE import_jobs
            SET status = 'failed', error_message = :error
            WHERE id = :job_id
            """,
            {"job_id": job_id, "error": str(e)},
        )
        db.commit()
        raise
    finally:
        db.close()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="worker.tasks.dropbox.process_single_file",
)
def process_single_file(self, job_id: str, shared_link: str, file_info: Dict[str, Any]):
    """
    Process a single file: download from Dropbox and upload to Supabase.
    """
    file_id = file_info.get("id", "")
    file_name = file_info["name"]
    file_path = file_info.get("path_display", file_info.get("path_lower", ""))
    file_size = int(file_info.get("size", 0))

    # Determine MIME type from extension
    ext = file_name.lower().split(".")[-1] if "." in file_name else ""
    mime_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "tiff": "image/tiff",
    }
    mime_type = mime_types.get(ext, "image/jpeg")

    logger.info(f"Processing file: {file_name} ({file_path})")

    db = get_db()

    try:
        # Download file from Dropbox
        dropbox_service = DropboxService()
        file_content = dropbox_service.download_shared_file(shared_link, file_path)

        # Upload to Supabase Storage
        storage_service = SupabaseStorageService()
        upload_result = storage_service.upload_file(
            file_content=file_content,
            file_name=file_name,
            mime_type=mime_type,
            folder="dropbox",
        )

        # Insert image record
        db.execute(
            """
            INSERT INTO images (
                name, dropbox_id, source, size, mime_type,
                storage_path, storage_url, import_job_id, status
            ) VALUES (
                :name, :dropbox_id, 'dropbox', :size, :mime_type,
                :storage_path, :storage_url, :job_id, 'completed'
            )
            """,
            {
                "name": file_name,
                "dropbox_id": file_id,
                "size": file_size,
                "mime_type": mime_type,
                "storage_path": upload_result["storage_path"],
                "storage_url": upload_result["storage_url"],
                "job_id": job_id,
            },
        )

        # Update job progress
        db.execute(
            """
            UPDATE import_jobs
            SET processed_files = processed_files + 1
            WHERE id = :job_id
            """,
            {"job_id": job_id},
        )
        db.commit()

        # Check if job is complete
        check_job_completion(job_id)

        logger.info(f"Successfully processed file: {file_name}")
        return {"status": "success", "file_name": file_name}

    except Exception as e:
        logger.error(f"Error processing file {file_name}: {str(e)}")

        # Update failed count
        db.execute(
            """
            UPDATE import_jobs
            SET failed_files = failed_files + 1
            WHERE id = :job_id
            """,
            {"job_id": job_id},
        )
        db.commit()

        # Check if job is complete (even with failures)
        check_job_completion(job_id)

        raise
    finally:
        db.close()


def check_job_completion(job_id: str):
    """Check if job is complete and update status."""
    db = get_db()
    try:
        result = db.execute(
            """
            SELECT total_files, processed_files, failed_files
            FROM import_jobs WHERE id = :job_id
            """,
            {"job_id": job_id},
        ).fetchone()

        if result:
            total, processed, failed = result
            if processed + failed >= total:
                status = "completed" if failed == 0 else "completed_with_errors"
                db.execute(
                    """
                    UPDATE import_jobs
                    SET status = :status, completed_at = :now
                    WHERE id = :job_id
                    """,
                    {"job_id": job_id, "status": status, "now": datetime.utcnow()},
                )
                db.commit()
    finally:
        db.close()
