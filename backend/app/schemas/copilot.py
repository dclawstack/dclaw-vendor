import uuid
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    # Optional focus — e.g. the copilot opened on a vendor's detail page.
    vendor_id: uuid.UUID | None = None


class CopilotReply(BaseModel):
    """Structured copilot answer (LLM JSON-mode target + API response)."""

    reply: str = Field(description="the assistant's answer, in plain prose")
    suggested_actions: list[str] = Field(
        default_factory=list,
        description="up to 3 short next-step suggestions for the user",
    )
