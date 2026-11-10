"""Environment-backed settings for the backend shell."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings with safe local defaults and no secret defaults."""

    app_name: str = "Enterprise Agentic RAG Backend"
    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_prefix="BACKEND_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return one process-local settings instance."""

    return Settings()
