"""Web data enrichment for vendor profiles (V3.2).

Best-effort: if the vendor has a website (or an email domain we can derive one
from), fetch the homepage and let the LLM extract a structured profile from the
page text — provenance ``source="web"``. If there's no usable URL or the fetch
fails, fall back to the LLM inferring the profile from the vendor name —
provenance ``source="inferred"`` so callers can tell the two apart.

The enrichment blob written onto ``Vendor.enrichment`` is the profile fields plus
provenance (source, fetched_url, enriched_at).
"""

from __future__ import annotations

import re

import httpx

from app.core.utils import utc_now
from app.models.vendor import Vendor
from app.schemas.enrichment import EnrichedProfile
from app.services.llm import LLMService

_SYSTEM = (
    "You extract a concise company profile for a vendor-management directory. "
    "Use only information supported by the provided text; leave a field null if "
    "it isn't supported. Keep the description to one sentence."
)

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def derive_url(vendor: Vendor) -> str | None:
    """A usable homepage URL from the website field or the email domain."""
    if vendor.website:
        url = vendor.website.strip()
        return url if url.startswith("http") else f"https://{url}"
    if vendor.email and "@" in vendor.email:
        domain = vendor.email.split("@", 1)[1].strip()
        # skip generic mailbox providers — they aren't the vendor's site
        if domain and domain.lower() not in _GENERIC_DOMAINS:
            return f"https://{domain}"
    return None


_GENERIC_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}


async def _fetch_text(url: str, *, timeout: float = 10.0) -> str:
    async with httpx.AsyncClient(
        timeout=timeout, follow_redirects=True, headers={"User-Agent": "dclaw-vendor/1.0"}
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        html = resp.text
    text = _WS_RE.sub(" ", _TAG_RE.sub(" ", html)).strip()
    return text[:4000]


async def enrich_vendor(llm: LLMService, vendor: Vendor) -> dict:
    """Return the enrichment blob (profile + provenance) for a vendor."""
    url = derive_url(vendor)
    source = "inferred"
    fetched_url: str | None = None
    if url:
        try:
            page_text = await _fetch_text(url)
            if page_text:
                prompt = (
                    f"Extract a profile for vendor '{vendor.name}' from its website text:\n\n"
                    f"{page_text}"
                )
                source, fetched_url = "web", url
            else:
                prompt = _inferred_prompt(vendor)
        except httpx.HTTPError:
            prompt = _inferred_prompt(vendor)
    else:
        prompt = _inferred_prompt(vendor)

    profile = await llm.structured(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
        EnrichedProfile,
    )
    return {
        **profile.model_dump(),
        "source": source,
        "fetched_url": fetched_url,
        "enriched_at": utc_now().isoformat(),
    }


def _inferred_prompt(vendor: Vendor) -> str:
    return (
        f"No website text is available. Infer a best-effort profile for the vendor "
        f"named '{vendor.name}'"
        + (f" (email {vendor.email})" if vendor.email else "")
        + ". Only fill fields you are reasonably confident about; otherwise leave null."
    )
