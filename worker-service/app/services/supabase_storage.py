import uuid
from typing import Optional
from supabase import create_client, Client
from ..config import get_settings

settings = get_settings()


class SupabaseStorageService:
    """Service for uploading files to Supabase Storage."""

    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key,  # Use service key for uploads
        )
        self.bucket = settings.supabase_storage_bucket

    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        mime_type: str,
        folder: Optional[str] = None,
    ) -> dict:
        """
        Upload a file to Supabase Storage.

        Args:
            file_content: The file content as bytes
            file_name: Original file name
            mime_type: MIME type of the file
            folder: Optional folder path within the bucket

        Returns:
            Dict with storage_path and storage_url
        """
        # Generate unique filename to avoid collisions
        unique_id = str(uuid.uuid4())[:8]
        safe_name = file_name.replace(" ", "_")
        storage_path = f"{folder}/{unique_id}_{safe_name}" if folder else f"{unique_id}_{safe_name}"

        # Upload to Supabase Storage
        response = self.client.storage.from_(self.bucket).upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": mime_type},
        )

        # Get public URL
        storage_url = self.client.storage.from_(self.bucket).get_public_url(
            storage_path
        )

        return {
            "storage_path": storage_path,
            "storage_url": storage_url,
        }

    def delete_file(self, storage_path: str) -> bool:
        """Delete a file from Supabase Storage."""
        try:
            self.client.storage.from_(self.bucket).remove([storage_path])
            return True
        except Exception:
            return False

    def file_exists(self, storage_path: str) -> bool:
        """Check if a file exists in storage."""
        try:
            self.client.storage.from_(self.bucket).download(storage_path)
            return True
        except Exception:
            return False
