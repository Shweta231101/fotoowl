from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

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

    # API Settings
    api_title: str = "Image Import API"
    api_version: str = "1.0.0"
    api_description: str = "Scalable image import system from Google Drive and Dropbox"

    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
