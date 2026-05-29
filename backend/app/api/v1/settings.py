from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.settings import LLMSettingsRead, LLMSettingsUpdate
from app.services import settings_service

router = APIRouter()


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
