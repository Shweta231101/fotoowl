from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class ImportRequest(BaseModel):
    """Request schema for import endpoints."""

    folder_url: str = Field(..., description="Public folder URL from Google Drive or Dropbox")


class ImportResponse(BaseModel):
    """Response schema for import endpoints."""

    job_id: str
    status: str
    message: str


class ImageResponse(BaseModel):
    """Response schema for a single image."""

    id: int
    name: str
    google_drive_id: Optional[str] = None
    dropbox_id: Optional[str] = None
    source: str
    size: int
    mime_type: str
    storage_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class ImageListResponse(BaseModel):
    """Response schema for paginated image list."""

    images: List[ImageResponse]
    total: int
    page: int
    pages: int
    page_size: int


class JobStatusResponse(BaseModel):
    """Response schema for job status."""

    job_id: str
    status: str
    source: str
    source_url: str
    total_files: int
    processed_files: int
    failed_files: int
    progress_percent: float
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
