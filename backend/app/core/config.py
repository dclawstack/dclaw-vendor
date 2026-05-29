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

    # ----- LLM providers (V2.1) -----------------------------------------
    # These are the initial/default values. They can be configured at runtime
    # from the app Settings page (persisted in the app_settings table, which
    # overrides these). Env names: LLM_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL,
    # OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL.
    #
    # provider: "ollama" (local primary), "openrouter" (cloud), or "auto"
    # (try Ollama first, fall back to OpenRouter).
    llm_provider: str = "auto"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    openrouter_api_key: str = ""
    openrouter_model: str = "moonshotai/kimi-k2"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # ----- Document storage (V4.2) --------------------------------------
    # backend: "local" (filesystem, default — dev/CI) or "minio" (S3-compatible
    # object store). MinIO is wired but only activates when STORAGE_BACKEND=minio
    # and the connection vars below are set; drop in real creds to go live.
    storage_backend: str = "local"
    storage_dir: str = "/tmp/dclaw_vendor_uploads"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_bucket: str = "vendor-docs"
    minio_secure: bool = False
    # Base URL the app is reachable at, used to build local download links.
    public_base_url: str = "http://localhost:8146"

    # ----- ERP / procurement integration (V6.4) -------------------------
    # backend: "mock" (sample data, default — dev/CI) or "http" (real ERP REST API).
    # The HTTP connector is wired but only activates when ERP_BACKEND=http and the
    # connection vars are set; drop in real creds to go live.
    erp_backend: str = "mock"
    erp_base_url: str = ""
    erp_api_key: str = ""

    # ----- Auth (Logto, V8.1) -------------------------------------------
    # Disabled by default (dev/CI run open). Set AUTH_ENABLED=true + the Logto
    # vars to enforce JWT validation on protected routes.
    auth_enabled: bool = False
    logto_endpoint: str = ""  # e.g. https://your-tenant.logto.app
    logto_app_id: str = ""
    logto_audience: str = ""  # API resource indicator

    # ----- Billing (Stripe, V8.2) ---------------------------------------
    # backend: "mock" (default) or "stripe". The Stripe backend activates when
    # STRIPE_API_KEY is set; per-seat price via STRIPE_PRICE_ID.
    billing_backend: str = "mock"
    stripe_api_key: str = ""
    stripe_price_id: str = ""
    billing_success_url: str = "http://localhost:3060/settings?billing=success"
    billing_cancel_url: str = "http://localhost:3060/settings?billing=cancel"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
