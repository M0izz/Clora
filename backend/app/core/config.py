from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable fallback."""

    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./storage/indusai.db"
    STORAGE_DIR: Path = Path("./storage")
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"
    OLLAMA_TIMEOUT_SEC: float = 60.0
    INTERNAL_SERVICE_KEY: str = "indusai-internal-worker-key-dev"
    MAX_FILE_SIZE_MB: int = 50
    SYNC_QUERY_TIMEOUT_SEC: int = 15
    INGESTION_CHUNK_SIZE: int = 500
    INGESTION_CHUNK_OVERLAP: int = 50
    ALLOWED_EXTENSIONS: list[str] = [
        ".pdf",
        ".docx",
        ".pptx",
        ".csv",
        ".xlsx",
        ".xls",
        ".json",
        ".png",
        ".jpg",
        ".jpeg",
        ".tiff",
        ".svg",
        ".txt",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
