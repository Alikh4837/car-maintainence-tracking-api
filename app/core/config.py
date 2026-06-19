from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    Values are read from environment variables / a .env file if present,
    falling back to the defaults below — handy for a zero-config demo.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Car Maintenance Tracker API"
    app_version: str = "1.0.0"
    debug: bool = True

    # SQLite keeps the demo dependency-free; swap for a Postgres URL in production.
    database_url: str = "sqlite:///./car_maintenance.db"


@lru_cache
def get_settings() -> Settings:
    """Cached so Settings() is only constructed once per process."""
    return Settings()


settings = get_settings()
