import httpx
from typing import List, Dict, Any, Optional
from ..config import get_settings

settings = get_settings()


class DropboxService:
    """Service for interacting with Dropbox API."""

    # Dropbox API base URL
    API_URL = "https://api.dropboxapi.com/2"
    CONTENT_URL = "https://content.dropboxapi.com/2"

    # Image extensions we support
    IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"]

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or settings.dropbox_access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        self.client = httpx.Client(timeout=30.0)

    def list_shared_folder_files(
        self, shared_link: str, path: str = ""
    ) -> List[Dict[str, Any]]:
        """
        List all image files in a shared Dropbox folder.

        Args:
            shared_link: The shared folder URL
            path: Relative path within the shared folder

        Returns:
            List of file metadata
        """
        all_files = []
        has_more = True
        cursor = None

        while has_more:
            if cursor:
                # Continue listing with cursor
                response = self.client.post(
                    f"{self.API_URL}/files/list_folder/continue",
                    headers=self.headers,
                    json={"cursor": cursor},
                )
            else:
                # Initial listing
                response = self.client.post(
                    f"{self.API_URL}/files/list_folder",
                    headers=self.headers,
                    json={
                        "path": path,
                        "shared_link": {"url": shared_link},
                        "recursive": True,
                        "include_media_info": True,
                        "limit": 100,
                    },
                )

            response.raise_for_status()
            data = response.json()

            # Filter for image files
            entries = data.get("entries", [])
            for entry in entries:
                if entry.get(".tag") == "file":
                    name = entry.get("name", "").lower()
                    if any(name.endswith(ext) for ext in self.IMAGE_EXTENSIONS):
                        all_files.append(entry)

            has_more = data.get("has_more", False)
            cursor = data.get("cursor")

        return all_files

    def download_shared_file(self, shared_link: str, path: str) -> bytes:
        """
        Download a file from a shared Dropbox link.

        Args:
            shared_link: The shared folder URL
            path: Path to the file within the shared folder

        Returns:
            File content as bytes
        """
        import json

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Dropbox-API-Arg": json.dumps({
                "url": shared_link,
                "path": path,
            }),
        }

        response = self.client.post(
            f"{self.CONTENT_URL}/sharing/get_shared_link_file",
            headers=headers,
        )
        response.raise_for_status()

        return response.content

    def get_shared_link_metadata(self, shared_link: str) -> Dict[str, Any]:
        """Get metadata for a shared link."""
        response = self.client.post(
            f"{self.API_URL}/sharing/get_shared_link_metadata",
            headers=self.headers,
            json={"url": shared_link},
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
