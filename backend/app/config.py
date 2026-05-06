from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://user:pass@localhost/dclaw_vendor"
    debug: bool = False

    class Config:
        env_prefix = "DCLAW_VENDOR_"

settings = Settings()
