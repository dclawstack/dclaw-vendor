"""App settings (LLM provider configuration).

The settings live in a single `app_settings` row. On first access the row is
seeded from `app.core.config` defaults (so env vars like OPENROUTER_API_KEY flow
through), and the Settings page overrides them at runtime thereafter.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings as env_settings
from app.models.app_setting import SETTINGS_SINGLETON_ID, AppSetting
from app.schemas.settings import LLMSettingsRead, LLMSettingsUpdate


@dataclass
class LLMConfig:
    """Resolved LLM config for the service layer (V2.x) — includes the real key."""

    provider: str
    ollama_base_url: str
    ollama_model: str
    openrouter_api_key: str
    openrouter_model: str
    openrouter_base_url: str


async def get_settings_row(db: AsyncSession) -> AppSetting:
    row = await db.get(AppSetting, SETTINGS_SINGLETON_ID)
    if row is None:
        row = AppSetting(
            id=SETTINGS_SINGLETON_ID,
            llm_provider=env_settings.llm_provider,
            ollama_base_url=env_settings.ollama_base_url,
            ollama_model=env_settings.ollama_model,
            openrouter_api_key=env_settings.openrouter_api_key,
            openrouter_model=env_settings.openrouter_model,
            openrouter_base_url=env_settings.openrouter_base_url,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
    return row


async def update_settings(db: AsyncSession, payload: LLMSettingsUpdate) -> AppSetting:
    row = await get_settings_row(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(row, field, value)
    await db.commit()
    await db.refresh(row)
    return row


def mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "••••"
    return f"{key[:4]}••••{key[-4:]}"


def to_read(row: AppSetting) -> LLMSettingsRead:
    return LLMSettingsRead(
        llm_provider=row.llm_provider,  # type: ignore[arg-type]
        ollama_base_url=row.ollama_base_url,
        ollama_model=row.ollama_model,
        openrouter_model=row.openrouter_model,
        openrouter_base_url=row.openrouter_base_url,
        openrouter_api_key_set=bool(row.openrouter_api_key),
        openrouter_api_key_preview=mask_key(row.openrouter_api_key),
        updated_at=row.updated_at,
    )


def to_config(row: AppSetting) -> LLMConfig:
    return LLMConfig(
        provider=row.llm_provider,
        ollama_base_url=row.ollama_base_url,
        ollama_model=row.ollama_model,
        openrouter_api_key=row.openrouter_api_key,
        openrouter_model=row.openrouter_model,
        openrouter_base_url=row.openrouter_base_url,
    )
