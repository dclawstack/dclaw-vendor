"""Survey feedback analysis (Phase 7, V7.3).

AI sentiment analysis for a single response comment, plus deterministic
aggregation of a vendor's feedback into counts, averages, and a monthly trend.
"""

from __future__ import annotations

from collections import defaultdict

from app.models.survey import Survey, SurveyResponse
from app.schemas.survey import SentimentResult, SentimentTrendPoint, VendorSentiment
from app.services.llm import LLMService

_SYSTEM = (
    "You are a customer-feedback analyst. Classify the sentiment of a stakeholder's "
    "comment about a vendor as positive, neutral, or negative, with a score from -1 "
    "(very negative) to 1 (very positive)."
)


async def analyze_sentiment(llm: LLMService, comment: str) -> SentimentResult:
    return await llm.structured(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Comment:\n{comment}"},
        ],
        SentimentResult,
    )


def aggregate(vendor_id, surveys: list[Survey]) -> VendorSentiment:
    responses: list[SurveyResponse] = [r for s in surveys for r in s.responses]
    count = len(responses)
    if count == 0:
        return VendorSentiment(
            vendor_id=vendor_id,
            response_count=0,
            average_rating=None,
            average_sentiment=None,
            positive=0,
            neutral=0,
            negative=0,
            trend=[],
        )

    avg_rating = round(sum(r.rating for r in responses) / count, 2)
    scored = [r.sentiment_score for r in responses if r.sentiment_score is not None]
    avg_sent = round(sum(scored) / len(scored), 3) if scored else None
    pos = sum(1 for r in responses if r.sentiment == "positive")
    neu = sum(1 for r in responses if r.sentiment == "neutral")
    neg = sum(1 for r in responses if r.sentiment == "negative")

    by_month: dict[str, list[SurveyResponse]] = defaultdict(list)
    for r in responses:
        by_month[r.created_at.strftime("%Y-%m")].append(r)
    trend = []
    for month in sorted(by_month):
        rs = by_month[month]
        ss = [r.sentiment_score for r in rs if r.sentiment_score is not None]
        trend.append(
            SentimentTrendPoint(
                period=month,
                average_rating=round(sum(r.rating for r in rs) / len(rs), 2),
                average_sentiment=round(sum(ss) / len(ss), 3) if ss else None,
                count=len(rs),
            )
        )

    return VendorSentiment(
        vendor_id=vendor_id,
        response_count=count,
        average_rating=avg_rating,
        average_sentiment=avg_sent,
        positive=pos,
        neutral=neu,
        negative=neg,
        trend=trend,
    )
