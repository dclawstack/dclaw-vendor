import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.utils import utc_now
from app.models.base import Base

# Fixed primary key for the singleton settings row.
SETTINGS_SINGLETON_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class AppSetting(Base):
    """Runtime-configurable application settings (single row).

    Holds LLM provider configuration set from the Settings page; values seed
    from `app.core.config` defaults on first access and override them thereafter.
    """

    __tablename__ = "app_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    llm_provider: Mapped[str] = mapped_column(String(20), default="auto", nullable=False)
    ollama_base_url: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    ollama_model: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    openrouter_api_key: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    openrouter_model: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    openrouter_base_url: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)
