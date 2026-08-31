"""
Centralized configuration for the INDUSAI-X backend.
All tunables live here; override via environment variables prefixed INDUSAI_.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Ollama connection
    ollama_base_url: str = "http://localhost:11434"
    request_timeout: int = 120          # seconds per inference call
    connect_timeout: int = 5            # seconds to establish connection

    # Generation defaults
    max_tokens: int = 2048
    temperature: float = 0.3            # keep output deterministic-ish for gov docs
    top_p: float = 0.9

    # Server
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]     # tighten in production

    class Config:
        env_prefix = "INDUSAI_"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
