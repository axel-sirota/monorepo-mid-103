from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # Don't treat `model_` prefix as the pydantic protected namespace.
        protected_namespaces=(),
    )

    model_path: str = "/models/churn.joblib"
    log_level: str = "INFO"
    model_version: str = "v1"


def get_settings() -> Settings:
    return Settings()
