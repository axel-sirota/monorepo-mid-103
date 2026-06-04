"""Application settings, sourced from environment variables."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    database_url: str = Field(
        default="postgresql+asyncpg://monorepo:monorepo@localhost:5432/users_db",
        description="Async SQLAlchemy URL.",
    )
    inference_gateway_url: str = Field(default="http://inference-gateway:9000")
    inference_api_key: str = Field(default="dev-key-change-me")
    log_level: str = Field(default="INFO")
    run_migrations_on_startup: bool = Field(default=True)
    inference_timeout_seconds: float = Field(default=5.0)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
