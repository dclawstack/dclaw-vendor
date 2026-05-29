from datetime import datetime
from typing import Literal

from pydantic import BaseModel

LLMProvider = Literal["ollama", "openrouter", "auto"]


class LLMSettingsRead(BaseModel):
    """LLM provider config as shown in the UI. The OpenRouter key is never
    returned in full — only whether it is set and a masked preview."""

    llm_provider: LLMProvider
    ollama_base_url: str
    ollama_model: str
    openrouter_model: str
    openrouter_base_url: str
    openrouter_api_key_set: bool
    openrouter_api_key_preview: str
    updated_at: datetime


class LLMSettingsUpdate(BaseModel):
    llm_provider: LLMProvider | None = None
    ollama_base_url: str | None = None
    ollama_model: str | None = None
    openrouter_api_key: str | None = None
    openrouter_model: str | None = None
    openrouter_base_url: str | None = None
