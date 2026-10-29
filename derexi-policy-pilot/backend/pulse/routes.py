
# backend/pulse/routes.py
from fastapi import APIRouter

from .service import get_feed

router = APIRouter(prefix="/api/pulse", tags=["Pulse"])


@router.get("")
def pulse_feed():
    """Return government updates in a common format."""
    return get_feed()


@router.get("/health")
def pulse_health():
    """Confirm the Pulse module is installed."""
    return {
        "feature": "Pulse",
        "status": "module loaded",
    }
