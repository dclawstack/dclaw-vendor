"""LLM service layer (V2.1).

Provider-agnostic async client with two backends:
- **Ollama** (local primary) — `{base}/api/chat`
- **OpenRouter** (cloud fallback, e.g. Kimi K2) — `{base}/chat/completions`

Provider selection is config-driven (`LLMConfig` resolved from the app settings):
- ``ollama``     → Ollama only
- ``openrouter`` → OpenRouter only
- ``auto``       → try Ollama first, fall back to OpenRouter if it fails and a key is set

`structured()` is a helper that returns a validated Pydantic model using each
provider's JSON mode, retrying once if the model returns invalid JSON.
"""

from __future__ import annotations

import json
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.services.settings_service import LLMConfig

T = TypeVar("T", bound=BaseModel)

Message = dict[str, str]  # {"role": "system"|"user"|"assistant", "content": ...}


class LLMError(Exception):
    """Raised when no configured provider can satisfy a request."""


class LLMService:
    def __init__(self, config: LLMConfig, *, timeout: float = 60.0):
        self.config = config
        self.timeout = timeout

    # -- public API ------------------------------------------------------

    async def chat(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> str:
        """Return the assistant's text reply, honoring the provider selection."""
        provider = self.config.provider
        if provider == "ollama":
            return await self._ollama_chat(messages, temperature, json_mode)
        if provider == "openrouter":
            return await self._openrouter_chat(messages, temperature, json_mode)

        # auto: Ollama first, then OpenRouter
        try:
            return await self._ollama_chat(messages, temperature, json_mode)
        except (httpx.HTTPError, LLMError) as ollama_err:
            if not self.config.openrouter_api_key:
                raise LLMError(
                    f"Ollama unavailable and no OpenRouter key set: {ollama_err}"
                ) from ollama_err
            return await self._openrouter_chat(messages, temperature, json_mode)

    async def structured(
        self,
        messages: list[Message],
        schema: type[T],
        *,
        temperature: float = 0.0,
    ) -> T:
        """Return a validated instance of `schema` from a JSON-mode completion."""
        instruction = {
            "role": "system",
            "content": (
                "Respond ONLY with a single JSON object matching this JSON schema. "
                "No markdown, no prose.\nSchema:\n"
                + json.dumps(schema.model_json_schema())
            ),
        }
        convo = [instruction, *messages]
        last_err: Exception | None = None
        for _ in range(2):
            raw = await self.chat(convo, temperature=temperature, json_mode=True)
            try:
                return schema.model_validate_json(_strip_json(raw))
            except (ValidationError, json.JSONDecodeError) as e:
                last_err = e
                convo = [
                    *convo,
                    {"role": "assistant", "content": raw},
                    {
                        "role": "user",
                        "content": f"That was invalid ({e}). Return ONLY valid JSON for the schema.",
                    },
                ]
        raise LLMError(f"Could not get valid structured output: {last_err}")

    async def ping(self) -> dict[str, Any]:
        """Lightweight reachability check for the active provider(s)."""
        reply = await self.chat(
            [{"role": "user", "content": "Reply with the single word: ok"}],
            temperature=0.0,
        )
        return {"ok": True, "provider": self.config.provider, "sample": reply.strip()[:80]}

    # -- providers -------------------------------------------------------

    async def _ollama_chat(
        self, messages: list[Message], temperature: float, json_mode: bool
    ) -> str:
        if not self.config.ollama_base_url:
            raise LLMError("Ollama base URL not configured")
        payload: dict[str, Any] = {
            "model": self.config.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if json_mode:
            payload["format"] = "json"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.config.ollama_base_url.rstrip('/')}/api/chat", json=payload
            )
            resp.raise_for_status()
            data = resp.json()
        content = (data.get("message") or {}).get("content")
        if not content:
            raise LLMError("Ollama returned an empty response")
        return content

    async def _openrouter_chat(
        self, messages: list[Message], temperature: float, json_mode: bool
    ) -> str:
        if not self.config.openrouter_api_key:
            raise LLMError("OpenRouter API key not configured")
        payload: dict[str, Any] = {
            "model": self.config.openrouter_model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {self.config.openrouter_api_key}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.config.openrouter_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise LLMError(f"Unexpected OpenRouter response shape: {e}") from e


def _strip_json(text: str) -> str:
    """Best-effort: pull the JSON object out of a possibly fenced reply."""
    s = text.strip()
    if s.startswith("```"):
        s = s.split("```", 2)[1] if "```" in s[3:] else s.lstrip("`")
        s = s[4:] if s.lower().startswith("json") else s
    start, end = s.find("{"), s.rfind("}")
    if start != -1 and end != -1 and end > start:
        return s[start : end + 1]
    return s
