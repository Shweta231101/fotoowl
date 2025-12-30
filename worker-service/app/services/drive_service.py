import httpx
from typing import List, Dict, Any, Optional
from ..config import get_settings

settings = get_settings()


class GoogleDriveService:
    """Service for interacting with Google Drive API."""

    # Google Drive API base URL
    BASE_URL = "https://www.googleapis.com/drive/v3"

    # Image MIME types we support
    IMAGE_MIME_TYPES = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/bmp",
        "image/tiff",
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.google_api_key
        self.client = httpx.Client(timeout=30.0)

    def list_files_in_folder(
        self, folder_id: str, page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all image files in a public Google Drive folder.

        Returns:
            Dict with 'files' list and optional 'nextPageToken'
        """
        # Build query for images in folder
        query = f"'{folder_id}' in parents and trashed = false"

        # Add MIME type filter for images
        mime_query = " or ".join(
            [f"mimeType = '{mt}'" for mt in self.IMAGE_MIME_TYPES]
        )
        query += f" and ({mime_query})"

        params = {
            "q": query,
            "fields": "nextPageToken, files(id, name, mimeType, size)",
            "pageSize": 100,
            "key": self.api_key,
        }

        if page_token:
            params["pageToken"] = page_token

        response = self.client.get(f"{self.BASE_URL}/files", params=params)
        response.raise_for_status()

        return response.json()

    def get_all_files_in_folder(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        Get all image files in a folder, handling pagination.

        Returns:
            List of file metadata dicts
        """
        all_files = []
        page_token = None

        while True:
            result = self.list_files_in_folder(folder_id, page_token)
            files = result.get("files", [])
            all_files.extend(files)

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return all_files

    def download_file(self, file_id: str) -> bytes:
        """
        Download a file from Google Drive.

        Returns:
            File content as bytes
        """
        # For public files, we can use the direct download URL
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        response = self.client.get(download_url, follow_redirects=True)
        response.raise_for_status()

        return response.content

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific file."""
        params = {
            "fields": "id, name, mimeType, size",
            "key": self.api_key,
        }

        response = self.client.get(
            f"{self.BASE_URL}/files/{file_id}", params=params
        )
        response.raise_for_status()

        return response.json()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
