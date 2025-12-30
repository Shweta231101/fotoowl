from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Worker service settings loaded from environment variables."""

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    supabase_storage_bucket: str = "images"

    # Database
    database_url: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Google Drive API
    google_api_key: str = ""

    # Dropbox
    dropbox_access_token: str = ""

    # Worker settings
    chunk_size: int = 100  # Number of files to process in each batch
    max_retries: int = 3
    retry_delay: int = 5  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
