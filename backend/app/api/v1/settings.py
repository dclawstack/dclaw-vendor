from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.settings import LLMSettingsRead, LLMSettingsUpdate
from app.services import settings_service
from app.services.llm import LLMError, LLMService

router = APIRouter()


class LLMTestResult(BaseModel):
    ok: bool
    provider: str
    detail: str


@router.get("/llm", response_model=LLMSettingsRead)
async def get_llm_settings(db: AsyncSession = Depends(get_db)):
    row = await settings_service.get_settings_row(db)
    return settings_service.to_read(row)


@router.patch("/llm", response_model=LLMSettingsRead)
async def update_llm_settings(
    payload: LLMSettingsUpdate, db: AsyncSession = Depends(get_db)
):
    row = await settings_service.update_settings(db, payload)
    return settings_service.to_read(row)


@router.post("/llm/test", response_model=LLMTestResult)
async def test_llm_connection(db: AsyncSession = Depends(get_db)):
    """Ping the currently-configured provider so the Settings page can verify it."""
    row = await settings_service.get_settings_row(db)
    service = LLMService(settings_service.to_config(row))
    try:
        result = await service.ping()
        return LLMTestResult(
            ok=True, provider=result["provider"], detail=result["sample"] or "ok"
        )
    except (LLMError, Exception) as e:  # noqa: BLE001 — surface any failure to the UI
        return LLMTestResult(ok=False, provider=row.llm_provider, detail=str(e)[:300])
