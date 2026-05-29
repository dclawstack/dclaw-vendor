import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm
from app.core.database import get_db
from app.models.survey import Survey, SurveyResponse
from app.repositories.survey_repo import SurveyRepository
from app.repositories.vendor_repo import VendorRepository
from app.schemas.survey import (
    SurveyCreate,
    SurveyList,
    SurveyRead,
    SurveyResponseCreate,
    SurveyResponseRead,
    VendorSentiment,
)
from app.services import feedback
from app.services.llm import LLMError, LLMService

router = APIRouter()


async def _get_survey(db: AsyncSession, survey_id: uuid.UUID) -> Survey:
    survey = await SurveyRepository(db).get_by_id(survey_id)
    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey


@router.post("", response_model=SurveyRead, status_code=status.HTTP_201_CREATED)
async def create_survey(payload: SurveyCreate, db: AsyncSession = Depends(get_db)):
    if await VendorRepository(db).get_by_id(payload.vendor_id) is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    survey = Survey(vendor_id=payload.vendor_id, title=payload.title)
    db.add(survey)
    await db.commit()
    await db.refresh(survey)
    return survey


@router.get("", response_model=SurveyList)
async def list_surveys(
    vendor_id: uuid.UUID | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await SurveyRepository(db).list_surveys(vendor_id, limit, offset)
    return SurveyList(items=items, total=total)


@router.get("/vendors/{vendor_id}/sentiment", response_model=VendorSentiment)
async def vendor_sentiment(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    surveys = await SurveyRepository(db).for_vendor(vendor_id)
    return feedback.aggregate(vendor_id, surveys)


@router.get("/{survey_id}", response_model=SurveyRead)
async def get_survey(survey_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await _get_survey(db, survey_id)


@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(survey_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    survey = await _get_survey(db, survey_id)
    await db.delete(survey)
    await db.commit()


@router.post(
    "/{survey_id}/responses",
    response_model=SurveyResponseRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_response(
    survey_id: uuid.UUID,
    payload: SurveyResponseCreate,
    analyze: bool = True,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    await _get_survey(db, survey_id)
    response = SurveyResponse(
        survey_id=survey_id,
        respondent=payload.respondent,
        rating=payload.rating,
        comment=payload.comment,
    )
    # Best-effort sentiment: a comment present + analyze requested. LLM failure
    # leaves the response un-analyzed rather than failing the submission.
    if analyze and payload.comment:
        try:
            result = await feedback.analyze_sentiment(llm, payload.comment)
            response.sentiment = result.sentiment
            response.sentiment_score = result.score
        except LLMError:
            pass
    db.add(response)
    await db.commit()
    await db.refresh(response)
    return response
