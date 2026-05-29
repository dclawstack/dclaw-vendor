from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "DClaw Vendor"
    app_env: str = "dev"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_vendor"
    # Postgres schema for the app domain tables. Empty => default (public),
    # used by local/CI Postgres. On Neon the runtime sets DB_SCHEMA=vendor so
    # domain tables live in the `vendor` schema alongside the `tracking` schema.
    db_schema: str = ""

    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
