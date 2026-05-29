"""Phase 4 — Onboarding workflow: cases, documents (storage), AI checklist/validate,
approval state machine."""

import pytest

from app.api.deps import get_llm
from app.api.main import app
from app.services.llm import LLMError


class FakeLLM:
    def __init__(self, fail: bool = False):
        self.fail = fail

    async def structured(self, messages, schema):
        if self.fail:
            raise LLMError("llm down")
        if schema.__name__ == "GeneratedChecklist":
            return schema(
                items=[
                    {"item": "W-9 tax form", "doc_type": "w9", "required": True},
                    {"item": "Certificate of insurance", "doc_type": "insurance", "required": True},
                ]
            )
        if schema.__name__ == "DocumentValidation":
            text = messages[-1]["content"]
            bad = "BADDOC" in text
            return schema(
                valid=not bad,
                doc_type_detected="other" if bad else "w9",
                issues=["content does not match expected type"] if bad else [],
            )
        raise AssertionError(f"unexpected schema {schema.__name__}")


@pytest.fixture
def fake_llm():
    app.dependency_overrides[get_llm] = lambda: FakeLLM()
    yield
    app.dependency_overrides.pop(get_llm, None)


async def _vendor(client, name="Acme"):
    return (await client.post("/api/v1/vendors", json={"name": name})).json()["id"]


@pytest.mark.asyncio
async def test_create_case_default_steps(client):
    vid = await _vendor(client)
    r = await client.post("/api/v1/onboarding/cases", json={"vendor_id": vid})
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "collecting"
    assert [s["name"] for s in body["steps"]] == ["Compliance review", "Finance approval"]
    assert body["steps"][0]["status"] == "pending"


@pytest.mark.asyncio
async def test_create_case_missing_vendor_404(client):
    r = await client.post(
        "/api/v1/onboarding/cases",
        json={"vendor_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_custom_steps_and_list(client):
    vid = await _vendor(client)
    r = await client.post(
        "/api/v1/onboarding/cases",
        json={"vendor_id": vid, "steps": [{"name": "Legal", "approver_role": "legal"}]},
    )
    cid = r.json()["id"]
    assert len(r.json()["steps"]) == 1
    lst = await client.get("/api/v1/onboarding/cases", params={"vendor_id": vid})
    assert lst.json()["total"] == 1
    assert lst.json()["items"][0]["id"] == cid


@pytest.mark.asyncio
async def test_generate_checklist(client, fake_llm):
    vid = await _vendor(client)
    cid = (await client.post("/api/v1/onboarding/cases", json={"vendor_id": vid})).json()["id"]
    r = await client.post(f"/api/v1/onboarding/cases/{cid}/checklist")
    assert r.status_code == 200
    checklist = r.json()["checklist"]
    assert len(checklist) == 2
    assert checklist[0]["doc_type"] == "w9"


@pytest.mark.asyncio
async def test_upload_download_and_validate(client, fake_llm):
    vid = await _vendor(client)
    cid = (await client.post("/api/v1/onboarding/cases", json={"vendor_id": vid})).json()["id"]
    up = await client.post(
        f"/api/v1/onboarding/cases/{cid}/documents",
        data={"doc_type": "w9"},
        files={"file": ("w9.txt", b"This is a W-9 tax form for Acme.", "text/plain")},
    )
    assert up.status_code == 201
    doc = up.json()
    assert doc["status"] == "uploaded" and doc["size"] > 0

    # download via local backend
    url = await client.get(f"/api/v1/onboarding/documents/{doc['id']}/url")
    key = url.json()["url"].split("key=")[1]
    dl = await client.get("/api/v1/onboarding/documents/download", params={"key": key})
    assert dl.status_code == 200 and b"W-9" in dl.content

    # AI validation -> validated
    val = await client.post(f"/api/v1/onboarding/documents/{doc['id']}/validate")
    assert val.status_code == 200
    assert val.json()["status"] == "validated"
    assert val.json()["validation"]["valid"] is True


@pytest.mark.asyncio
async def test_validate_rejects_bad_doc(client, fake_llm):
    vid = await _vendor(client)
    cid = (await client.post("/api/v1/onboarding/cases", json={"vendor_id": vid})).json()["id"]
    up = await client.post(
        f"/api/v1/onboarding/cases/{cid}/documents",
        data={"doc_type": "w9"},
        files={"file": ("x.txt", b"BADDOC nonsense", "text/plain")},
    )
    val = await client.post(f"/api/v1/onboarding/documents/{up.json()['id']}/validate")
    assert val.json()["status"] == "rejected"
    assert val.json()["validation"]["issues"]


@pytest.mark.asyncio
async def test_full_approval_flow_activates_vendor(client):
    vid = await _vendor(client, "Globex")
    # vendor starts active by default; set inactive to prove activation flips it
    await client.patch(f"/api/v1/vendors/{vid}", json={"status": "inactive"})
    cid = (await client.post("/api/v1/onboarding/cases", json={"vendor_id": vid})).json()["id"]

    submitted = await client.post(f"/api/v1/onboarding/cases/{cid}/submit")
    assert submitted.json()["status"] == "pending_approval"
    steps = sorted(submitted.json()["steps"], key=lambda s: s["step_order"])

    # approve step 1
    r1 = await client.post(
        f"/api/v1/onboarding/steps/{steps[0]['id']}/decision",
        json={"decision": "approve", "decided_by": "alice"},
    )
    assert r1.json()["status"] == "pending_approval"
    # approve step 2 -> case approved
    r2 = await client.post(
        f"/api/v1/onboarding/steps/{steps[1]['id']}/decision",
        json={"decision": "approve", "decided_by": "bob"},
    )
    assert r2.json()["status"] == "approved"

    act = await client.post(f"/api/v1/onboarding/cases/{cid}/activate")
    assert act.json()["status"] == "activated"
    v = await client.get(f"/api/v1/vendors/{vid}")
    assert v.json()["status"] == "active"


@pytest.mark.asyncio
async def test_out_of_order_decision_409(client):
    vid = await _vendor(client)
    cid = (await client.post("/api/v1/onboarding/cases", json={"vendor_id": vid})).json()["id"]
    submitted = await client.post(f"/api/v1/onboarding/cases/{cid}/submit")
    steps = sorted(submitted.json()["steps"], key=lambda s: s["step_order"])
    # try to decide the second step first
    r = await client.post(
        f"/api/v1/onboarding/steps/{steps[1]['id']}/decision",
        json={"decision": "approve"},
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_rejection_path(client):
    vid = await _vendor(client)
    cid = (await client.post("/api/v1/onboarding/cases", json={"vendor_id": vid})).json()["id"]
    submitted = await client.post(f"/api/v1/onboarding/cases/{cid}/submit")
    steps = sorted(submitted.json()["steps"], key=lambda s: s["step_order"])
    r = await client.post(
        f"/api/v1/onboarding/steps/{steps[0]['id']}/decision",
        json={"decision": "reject", "comment": "missing insurance"},
    )
    assert r.json()["status"] == "rejected"
    # cannot activate a rejected case
    act = await client.post(f"/api/v1/onboarding/cases/{cid}/activate")
    assert act.status_code == 409


@pytest.mark.asyncio
async def test_delete_case_cascades(client):
    vid = await _vendor(client)
    cid = (await client.post("/api/v1/onboarding/cases", json={"vendor_id": vid})).json()["id"]
    await client.post(
        f"/api/v1/onboarding/cases/{cid}/documents",
        data={"doc_type": "w9"},
        files={"file": ("a.txt", b"hello", "text/plain")},
    )
    d = await client.delete(f"/api/v1/onboarding/cases/{cid}")
    assert d.status_code == 204
    assert (await client.get(f"/api/v1/onboarding/cases/{cid}")).status_code == 404
