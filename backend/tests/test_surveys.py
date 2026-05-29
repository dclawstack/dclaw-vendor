"""Phase 7 — V7.3 Survey & Feedback: responses, AI sentiment, aggregation."""

import pytest

from app.api.deps import get_llm
from app.api.main import app
from app.services.llm import LLMError


class FakeLLM:
    def __init__(self, sentiment="positive", score=0.8, fail=False):
        self.sentiment, self.score, self.fail = sentiment, score, fail

    async def structured(self, messages, schema):
        if self.fail:
            raise LLMError("llm down")
        assert schema.__name__ == "SentimentResult"
        return schema(sentiment=self.sentiment, score=self.score)


def use_llm(llm):
    app.dependency_overrides[get_llm] = lambda: llm


@pytest.fixture(autouse=True)
def _clear():
    yield
    app.dependency_overrides.pop(get_llm, None)


async def _survey(client, name="Acme"):
    vid = (await client.post("/api/v1/vendors", json={"name": name})).json()["id"]
    sid = (
        await client.post("/api/v1/surveys", json={"vendor_id": vid, "title": "Q2 feedback"})
    ).json()["id"]
    return vid, sid


@pytest.mark.asyncio
async def test_create_survey_missing_vendor_404(client):
    r = await client.post(
        "/api/v1/surveys",
        json={"vendor_id": "00000000-0000-0000-0000-000000000000", "title": "x"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_add_response_with_sentiment(client):
    use_llm(FakeLLM(sentiment="positive", score=0.9))
    _, sid = await _survey(client)
    r = await client.post(
        f"/api/v1/surveys/{sid}/responses",
        json={"respondent": "ops", "rating": 5, "comment": "Excellent and reliable"},
    )
    assert r.status_code == 201
    assert r.json()["sentiment"] == "positive"
    assert r.json()["sentiment_score"] == 0.9


@pytest.mark.asyncio
async def test_response_without_comment_skips_llm(client):
    use_llm(FakeLLM(fail=True))  # would raise if called
    _, sid = await _survey(client)
    r = await client.post(f"/api/v1/surveys/{sid}/responses", json={"rating": 4})
    assert r.status_code == 201
    assert r.json()["sentiment"] is None


@pytest.mark.asyncio
async def test_sentiment_failure_does_not_block_submission(client):
    use_llm(FakeLLM(fail=True))
    _, sid = await _survey(client)
    r = await client.post(
        f"/api/v1/surveys/{sid}/responses", json={"rating": 2, "comment": "meh"}
    )
    assert r.status_code == 201
    assert r.json()["sentiment"] is None


@pytest.mark.asyncio
async def test_vendor_sentiment_aggregate(client):
    vid, sid = await _survey(client)
    use_llm(FakeLLM(sentiment="positive", score=1.0))
    await client.post(f"/api/v1/surveys/{sid}/responses", json={"rating": 5, "comment": "great"})
    use_llm(FakeLLM(sentiment="negative", score=-0.6))
    await client.post(f"/api/v1/surveys/{sid}/responses", json={"rating": 1, "comment": "bad"})

    r = await client.get(f"/api/v1/surveys/vendors/{vid}/sentiment")
    body = r.json()
    assert body["response_count"] == 2
    assert body["average_rating"] == 3.0
    assert body["positive"] == 1 and body["negative"] == 1
    assert body["average_sentiment"] == 0.2  # mean(1.0, -0.6)
    assert len(body["trend"]) == 1


@pytest.mark.asyncio
async def test_delete_survey_cascades(client):
    _, sid = await _survey(client)
    await client.post(f"/api/v1/surveys/{sid}/responses", json={"rating": 3})
    d = await client.delete(f"/api/v1/surveys/{sid}")
    assert d.status_code == 204
    assert (await client.get(f"/api/v1/surveys/{sid}")).status_code == 404
