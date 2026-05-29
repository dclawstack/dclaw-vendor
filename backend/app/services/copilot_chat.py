"""Copilot chat orchestration (V2.4).

Grounds the conversation in the live workspace context (from `retrieval`) and
asks the LLM for a structured `CopilotReply` (prose answer + up to 3 next-step
suggestions). Kept separate from the router so it can be unit-tested with a
mocked LLM and a plain context string.
"""

from __future__ import annotations

from app.schemas.copilot import ChatMessage, CopilotReply
from app.services.llm import LLMService

_SYSTEM = (
    "You are the DClaw Vendor Copilot, an assistant for a procurement team. "
    "Answer questions about vendors, purchase orders, spend, and onboarding using "
    "ONLY the workspace data provided below — do not invent vendors, numbers, or POs. "
    "If the data doesn't contain the answer, say so plainly. Be concise and practical. "
    "Also propose up to 3 short, concrete next actions the user could take.\n\n"
    "{context}"
)


async def run_chat(
    llm: LLMService, context: str, messages: list[ChatMessage]
) -> CopilotReply:
    convo = [
        {"role": "system", "content": _SYSTEM.format(context=context)},
        *[{"role": m.role, "content": m.content} for m in messages],
    ]
    return await llm.structured(convo, CopilotReply)
