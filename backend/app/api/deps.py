"""Shared FastAPI dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import settings_service
from app.services.llm import LLMService


async def get_llm(db: AsyncSession = Depends(get_db)) -> LLMService:
    """Resolve the configured LLM provider into a service instance."""
    row = await settings_service.get_settings_row(db)
    return LLMService(settings_service.to_config(row))
