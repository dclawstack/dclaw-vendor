import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm
from app.core.database import get_db
from app.models.enums import OnboardingStatus
from app.models.onboarding import ApprovalStep, OnboardingCase, OnboardingDocument
from app.repositories.onboarding_repo import OnboardingRepository
from app.repositories.vendor_repo import VendorRepository
from app.schemas.onboarding import (
    ApprovalDecision,
    OnboardingCaseCreate,
    OnboardingCaseList,
    OnboardingCaseRead,
    OnboardingDocumentRead,
)
from app.services import onboarding as flow
from app.services.llm import LLMError, LLMService
from app.services.storage import get_storage, make_key

router = APIRouter()


async def _get_case(db: AsyncSession, case_id: uuid.UUID) -> OnboardingCase:
    case = await OnboardingRepository(db).get_by_id(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Onboarding case not found")
    return case


# --- cases --------------------------------------------------------------


@router.post("/cases", response_model=OnboardingCaseRead, status_code=status.HTTP_201_CREATED)
async def create_case(payload: OnboardingCaseCreate, db: AsyncSession = Depends(get_db)):
    vendor = await VendorRepository(db).get_by_id(payload.vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    names_roles = (
        [(s.name, s.approver_role) for s in payload.steps]
        if payload.steps
        else list(flow.DEFAULT_STEPS)
    )
    case = OnboardingCase(
        vendor_id=payload.vendor_id,
        notes=payload.notes,
        status=OnboardingStatus.collecting,
        steps=flow.build_steps(names_roles),
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return case


@router.get("/cases", response_model=OnboardingCaseList)
async def list_cases(
    vendor_id: uuid.UUID | None = None,
    status: OnboardingStatus | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await OnboardingRepository(db).list_cases(
        vendor_id, status, limit, offset
    )
    return OnboardingCaseList(items=items, total=total)


@router.get("/cases/{case_id}", response_model=OnboardingCaseRead)
async def get_case(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await _get_case(db, case_id)


@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    case = await _get_case(db, case_id)
    storage = get_storage()
    for doc in case.documents:
        try:
            storage.delete(doc.storage_key)
        except Exception:  # noqa: BLE001 — best-effort cleanup
            pass
    await db.delete(case)
    await db.commit()


@router.post("/cases/{case_id}/checklist", response_model=OnboardingCaseRead)
async def generate_checklist(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    case = await _get_case(db, case_id)
    try:
        result = await flow.generate_checklist(llm, case.vendor)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e
    case.checklist = [item.model_dump() for item in result.items]
    await db.commit()
    await db.refresh(case)
    return case


@router.post("/cases/{case_id}/submit", response_model=OnboardingCaseRead)
async def submit_case(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    case = await _get_case(db, case_id)
    try:
        flow.submit_case(case)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    await db.commit()
    await db.refresh(case)
    return case


@router.post("/cases/{case_id}/activate", response_model=OnboardingCaseRead)
async def activate_case(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    case = await _get_case(db, case_id)
    try:
        flow.activate_case(case)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    await db.commit()
    await db.refresh(case)
    return case


# --- documents ----------------------------------------------------------


@router.post(
    "/cases/{case_id}/documents",
    response_model=OnboardingDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    case_id: uuid.UUID,
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    case = await _get_case(db, case_id)
    data = await file.read()
    key = make_key(str(case.id), file.filename or "upload.bin")
    get_storage().put(key, data, file.content_type)
    doc = OnboardingDocument(
        case_id=case.id,
        doc_type=doc_type,
        filename=file.filename or "upload.bin",
        storage_key=key,
        content_type=file.content_type,
        size=len(data),
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get("/documents/download")
async def download_document(key: str, db: AsyncSession = Depends(get_db)):
    """Local-backend download. (MinIO clients use the presigned URL instead.)"""
    try:
        data = get_storage().get(key)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="File not found") from e
    return Response(content=data, media_type="application/octet-stream")


@router.get("/documents/{doc_id}/url")
async def document_url(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    doc = await db.get(OnboardingDocument, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"url": get_storage().presigned_url(doc.storage_key)}


@router.post("/documents/{doc_id}/validate", response_model=OnboardingDocumentRead)
async def validate_document(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    doc = await db.get(OnboardingDocument, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        raw = get_storage().get(doc.storage_key)
        text = raw.decode("utf-8", errors="ignore")
    except FileNotFoundError:
        text = ""
    try:
        result = await flow.validate_document(llm, doc.doc_type, text)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e
    flow.apply_validation(doc, result)
    await db.commit()
    await db.refresh(doc)
    return doc


# --- approval steps -----------------------------------------------------


@router.post("/steps/{step_id}/decision", response_model=OnboardingCaseRead)
async def decide_step(
    step_id: uuid.UUID,
    payload: ApprovalDecision,
    db: AsyncSession = Depends(get_db),
):
    step = await db.get(ApprovalStep, step_id)
    if step is None:
        raise HTTPException(status_code=404, detail="Approval step not found")
    case = await _get_case(db, step.case_id)
    try:
        flow.decide_step(
            case,
            step,
            approve=payload.decision == "approve",
            decided_by=payload.decided_by,
            comment=payload.comment,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    await db.commit()
    await db.refresh(case)
    return case
