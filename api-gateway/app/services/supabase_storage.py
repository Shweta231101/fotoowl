import uuid
import httpx
from typing import Optional
from ..config import get_settings

settings = get_settings()


class SupabaseStorageService:
    """Service for uploading files to Supabase Storage using REST API."""

    def __init__(self):
        self.supabase_url = settings.supabase_url
        self.service_key = settings.supabase_service_key
        self.bucket = settings.supabase_storage_bucket
        self.client = httpx.Client(timeout=60.0)

    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        mime_type: str,
        folder: Optional[str] = None,
    ) -> dict:
        """
        Upload a file to Supabase Storage using REST API.

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

        # Supabase Storage REST API endpoint
        upload_url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{storage_path}"

        headers = {
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": mime_type,
            "x-upsert": "true",  # Overwrite if exists
        }

        response = self.client.post(
            upload_url,
            content=file_content,
            headers=headers,
        )
        response.raise_for_status()

        # Construct public URL
        storage_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{storage_path}"

        return {
            "storage_path": storage_path,
            "storage_url": storage_url,
        }

    def delete_file(self, storage_path: str) -> bool:
        """Delete a file from Supabase Storage."""
        try:
            delete_url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{storage_path}"
            headers = {
                "Authorization": f"Bearer {self.service_key}",
            }
            response = self.client.delete(delete_url, headers=headers)
            return response.status_code == 200
        except Exception:
            return False

    def file_exists(self, storage_path: str) -> bool:
        """Check if a file exists in storage."""
        try:
            url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{storage_path}"
            headers = {
                "Authorization": f"Bearer {self.service_key}",
            }
            response = self.client.head(url, headers=headers)
            return response.status_code == 200
        except Exception:
            return False

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
