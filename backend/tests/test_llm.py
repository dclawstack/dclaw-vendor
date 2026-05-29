import httpx
import pytest
from pydantic import BaseModel

from app.services.llm import LLMError, LLMService
from app.services.settings_service import LLMConfig


def cfg(provider: str, key: str = "") -> LLMConfig:
    return LLMConfig(
        provider=provider,
        ollama_base_url="http://ollama.test",
        ollama_model="m",
        openrouter_api_key=key,
        openrouter_model="om",
        openrouter_base_url="http://openrouter.test",
    )


class Foo(BaseModel):
    ok: bool
    n: int


@pytest.mark.asyncio
async def test_chat_uses_ollama_when_selected(monkeypatch):
    s = LLMService(cfg("ollama"))

    async def fake(messages, temperature, json_mode):
        return "hi from ollama"

    monkeypatch.setattr(s, "_ollama_chat", fake)
    assert await s.chat([{"role": "user", "content": "x"}]) == "hi from ollama"


@pytest.mark.asyncio
async def test_chat_uses_openrouter_when_selected(monkeypatch):
    s = LLMService(cfg("openrouter", key="sk"))

    async def fake(messages, temperature, json_mode):
        return "hi from openrouter"

    monkeypatch.setattr(s, "_openrouter_chat", fake)
    assert await s.chat([{"role": "user", "content": "x"}]) == "hi from openrouter"


@pytest.mark.asyncio
async def test_auto_falls_back_to_openrouter(monkeypatch):
    s = LLMService(cfg("auto", key="sk"))

    async def boom(messages, temperature, json_mode):
        raise httpx.ConnectError("no ollama")

    async def ok(messages, temperature, json_mode):
        return "from openrouter"

    monkeypatch.setattr(s, "_ollama_chat", boom)
    monkeypatch.setattr(s, "_openrouter_chat", ok)
    assert await s.chat([{"role": "user", "content": "x"}]) == "from openrouter"


@pytest.mark.asyncio
async def test_auto_without_key_raises(monkeypatch):
    s = LLMService(cfg("auto", key=""))

    async def boom(messages, temperature, json_mode):
        raise httpx.ConnectError("no ollama")

    monkeypatch.setattr(s, "_ollama_chat", boom)
    with pytest.raises(LLMError):
        await s.chat([{"role": "user", "content": "x"}])


@pytest.mark.asyncio
async def test_structured_parses_model(monkeypatch):
    s = LLMService(cfg("ollama"))

    async def fake(messages, temperature, json_mode):
        return '{"ok": true, "n": 5}'

    monkeypatch.setattr(s, "_ollama_chat", fake)
    out = await s.structured([{"role": "user", "content": "x"}], Foo)
    assert out.ok is True and out.n == 5


@pytest.mark.asyncio
async def test_structured_retries_on_bad_json(monkeypatch):
    s = LLMService(cfg("ollama"))
    calls = {"n": 0}

    async def fake(messages, temperature, json_mode):
        calls["n"] += 1
        return "not json at all" if calls["n"] == 1 else '{"ok": false, "n": 2}'

    monkeypatch.setattr(s, "_ollama_chat", fake)
    out = await s.structured([{"role": "user", "content": "x"}], Foo)
    assert out.n == 2 and calls["n"] == 2


@pytest.mark.asyncio
async def test_structured_strips_code_fence(monkeypatch):
    s = LLMService(cfg("ollama"))

    async def fake(messages, temperature, json_mode):
        return '```json\n{"ok": true, "n": 9}\n```'

    monkeypatch.setattr(s, "_ollama_chat", fake)
    out = await s.structured([{"role": "user", "content": "x"}], Foo)
    assert out.n == 9


@pytest.mark.asyncio
async def test_llm_test_endpoint_shape(client):
    # No live provider in CI -> endpoint catches the failure and returns ok=false,
    # but always 200 with the expected fields.
    resp = await client.post("/api/v1/settings/llm/test")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) == {"ok", "provider", "detail"}
    assert isinstance(body["ok"], bool)
