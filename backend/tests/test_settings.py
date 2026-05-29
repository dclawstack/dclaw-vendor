import pytest


@pytest.mark.asyncio
async def test_get_llm_settings_seeds_defaults(client):
    resp = await client.get("/api/v1/settings/llm")
    assert resp.status_code == 200
    body = resp.json()
    assert body["llm_provider"] == "auto"
    assert body["ollama_base_url"] == "http://localhost:11434"
    # raw key is never returned
    assert "openrouter_api_key" not in body
    assert body["openrouter_api_key_set"] is False
    assert body["openrouter_api_key_preview"] == ""


@pytest.mark.asyncio
async def test_update_llm_settings(client):
    resp = await client.patch(
        "/api/v1/settings/llm",
        json={
            "llm_provider": "ollama",
            "ollama_base_url": "http://ollama.local:11434",
            "ollama_model": "llama3.1:8b",
            "openrouter_api_key": "sk-or-v1-supersecrettoken1234",
            "openrouter_model": "moonshotai/kimi-k2",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["llm_provider"] == "ollama"
    assert body["ollama_base_url"] == "http://ollama.local:11434"
    assert body["ollama_model"] == "llama3.1:8b"
    # key is stored but only ever returned masked
    assert body["openrouter_api_key_set"] is True
    assert body["openrouter_api_key_preview"] == "sk-o••••1234"
    assert "openrouter_api_key" not in body

    # persisted across requests
    again = await client.get("/api/v1/settings/llm")
    assert again.json()["ollama_model"] == "llama3.1:8b"
    assert again.json()["openrouter_api_key_set"] is True


@pytest.mark.asyncio
async def test_partial_update_preserves_other_fields(client):
    await client.patch("/api/v1/settings/llm", json={"ollama_model": "mistral"})
    resp = await client.patch("/api/v1/settings/llm", json={"llm_provider": "openrouter"})
    assert resp.json()["ollama_model"] == "mistral"
    assert resp.json()["llm_provider"] == "openrouter"


@pytest.mark.asyncio
async def test_invalid_provider_rejected(client):
    resp = await client.patch("/api/v1/settings/llm", json={"llm_provider": "gpt"})
    assert resp.status_code == 422
