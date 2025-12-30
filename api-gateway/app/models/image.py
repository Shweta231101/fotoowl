from sqlalchemy import Column, Integer, String, BigInteger, Text, DateTime, Index
from sqlalchemy.sql import func
from ..database import Base


class Image(Base):
    """Model for storing imported image metadata."""

    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    google_drive_id = Column(String(255), nullable=True)
    dropbox_id = Column(String(255), nullable=True)
    source = Column(String(50), nullable=False)  # 'google_drive' or 'dropbox'
    size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    storage_path = Column(Text, nullable=False)
    storage_url = Column(Text, nullable=False)
    import_job_id = Column(String(255), nullable=True)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_images_source", "source"),
        Index("idx_images_job_id", "import_job_id"),
    )


class ImportJob(Base):
    """Model for tracking import job status."""

    __tablename__ = "import_jobs"

    id = Column(String(255), primary_key=True)
    source = Column(String(50), nullable=False)
    source_url = Column(Text, nullable=False)
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    failed_files = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (Index("idx_jobs_status", "status"),)
