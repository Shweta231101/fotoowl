from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from ..database import get_db
from ..models import Image
from ..schemas import ImageResponse, ImageListResponse
from ..config import get_settings

router = APIRouter(prefix="/images", tags=["Images"])
settings = get_settings()


@router.get("", response_model=ImageListResponse)
async def list_images(
    source: Optional[str] = Query(
        None,
        description="Filter by source: 'google_drive' or 'dropbox'",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(
        None,
        ge=1,
        le=settings.max_page_size,
        description=f"Items per page (max {settings.max_page_size})",
    ),
    db: Session = Depends(get_db),
):
    """
    Get a paginated list of all imported images.

    Supports filtering by source (google_drive or dropbox).
    """
    # Default page size
    if limit is None:
        limit = settings.default_page_size

    # Build query
    query = db.query(Image)

    # Apply source filter if provided
    if source:
        if source not in ["google_drive", "dropbox"]:
            # Return empty if invalid source
            return ImageListResponse(
                images=[],
                total=0,
                page=page,
                pages=0,
                page_size=limit,
            )
        query = query.filter(Image.source == source)

    # Get total count
    total = query.count()

    # Calculate pagination
    pages = (total + limit - 1) // limit if total > 0 else 0
    offset = (page - 1) * limit

    # Fetch images
    images = (
        query.order_by(Image.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return ImageListResponse(
        images=[ImageResponse.model_validate(img) for img in images],
        total=total,
        page=page,
        pages=pages,
        page_size=limit,
    )


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: int,
    db: Session = Depends(get_db),
):
    """Get a single image by ID."""
    image = db.query(Image).filter(Image.id == image_id).first()

    if not image:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Image not found")

    return ImageResponse.model_validate(image)
