"""Pulse: public regulatory-intelligence endpoints.

Read-only by design. Pulse is an information surface: it never writes to
Supabase, never changes policy records, and exposes no administrative actions.
"""

from fastapi import APIRouter, Query

from .service import DEFAULT_LIMIT, MAX_ARTICLES, get_feed

router = APIRouter(prefix="/api/pulse", tags=["Pulse"])


@router.get("")
def pulse_feed(
    limit: int = Query(
        DEFAULT_LIMIT,
        ge=1,
        le=MAX_ARTICLES,
        description="Maximum number of articles to return.",
    )
):
    """Return the combined government feed in a common article format.

    Individual source failures are reported in ``sources`` and never fail the
    request, so the page can render whatever did load.
    """
    return get_feed(limit=limit)


@router.get("/health")
def pulse_health():
    """Lightweight check that the Pulse module is installed and importable."""
    from .sources import SOURCES

    return {
        "feature": "Pulse",
        "status": "module loaded",
        "sources": list(SOURCES.keys()),
        "cache_seconds": 1800,
    }
