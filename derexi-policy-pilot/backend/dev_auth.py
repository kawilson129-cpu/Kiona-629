"""Development-only identity provider for DeRexi persona testing.

Why this exists
---------------
DeRexi's production identity path is a Supabase-issued JWT verified against the
project JWKS (see ``auth.py``). Supabase Auth has no seeded users yet, so local
development and automated tests need a *server-verified* way to switch personas
without hard-coded admin bypasses, pasted tokens, or real accounts.

This module mints short-lived HS256 tokens for an explicit allowlist of seeded
users. It is a development identity provider, not an authorization bypass:

  * it is only reachable when ``DEREXI_ENV`` is not ``production`` and
    ``DEREXI_DEV_AUTH`` is enabled;
  * the signing secret is generated per process (or supplied by an env var for
    multi-worker dev), never logged, and never exposed to the browser;
  * the token issuer/audience are distinct from Supabase, so a dev token cannot
    masquerade as a Supabase token;
  * every request still resolves the user from the database and applies the
    same role and ownership checks as the production path.

The router is mounted conditionally by ``main.py``; in production the module is
importable but the endpoints do not exist (404).
"""

from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

DEV_ISSUER = "derexi-dev"
DEV_AUDIENCE = "authenticated"
TOKEN_TTL_SECONDS = 15 * 60
ALLOWED_ALGORITHM = "HS256"

# A per-process secret is sufficient for a single local uvicorn process. For
# multiple dev workers, set DEREXI_DEV_AUTH_SECRET to the same value in each.
_PROCESS_SECRET = (os.getenv("DEREXI_DEV_AUTH_SECRET") or "").encode("utf-8") or secrets.token_bytes(32)

# ``config_router`` is always mounted (the UI needs to know which sign-in path
# exists). ``router`` is mounted only when development auth is enabled.
config_router = APIRouter(tags=["authentication"])
router = APIRouter(tags=["development identity"])


class DevTokenRequest(BaseModel):
    user_id: int


def _truthy(value: Optional[str]) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def current_environment() -> str:
    return (os.getenv("DEREXI_ENV") or "development").strip().lower()


def dev_auth_enabled() -> bool:
    """True only outside production with an explicit opt-in flag."""
    return current_environment() != "production" and _truthy(os.getenv("DEREXI_DEV_AUTH"))


def allowed_user_ids() -> set:
    """Parse DEREXI_DEV_USER_IDS; an empty value means all seeded users."""
    raw = (os.getenv("DEREXI_DEV_USER_IDS") or "").strip()
    if not raw:
        return set()
    ids = set()
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if chunk.isdigit():
            ids.add(int(chunk))
    return ids


def _is_loopback(host: Optional[str]) -> bool:
    # TestClient uses "testclient"; allow it only in the explicit test env.
    if host in {"127.0.0.1", "::1", "localhost"}:
        return True
    return host == "testclient" and current_environment() == "test"


def _require_dev_request(request: Request) -> None:
    if not dev_auth_enabled():
        # 404, not 403: production should not advertise the endpoint.
        raise HTTPException(status_code=404, detail="Not found")
    if not _is_loopback(request.client.host if request.client else None):
        raise HTTPException(status_code=403, detail="Development identity is loopback-only")


def issue_token(user_id: int, email: str, role: str) -> dict:
    """Mint a short-lived dev token. Returns token metadata, never the secret."""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=TOKEN_TTL_SECONDS)
    claims = {
        "sub": f"dev:{user_id}",
        "email": email,
        "role": role,
        "iss": DEV_ISSUER,
        "aud": DEV_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "jti": secrets.token_hex(12),
    }
    token = jwt.encode(claims, _PROCESS_SECRET, algorithm=ALLOWED_ALGORITHM)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_TTL_SECONDS,
        "issuer": DEV_ISSUER,
    }


def verify_token(token: str) -> dict:
    """Verify issuer, audience, expiry, and signature of a dev token."""
    if not dev_auth_enabled():
        raise ValueError("Development identity is disabled")
    claims = jwt.decode(
        token,
        _PROCESS_SECRET,
        algorithms=[ALLOWED_ALGORITHM],
        audience=DEV_AUDIENCE,
        issuer=DEV_ISSUER,
        options={
            "require": ["exp", "iat", "sub", "aud", "iss"],
            "verify_signature": True,
            "verify_exp": True,
            "verify_iat": True,
            "verify_aud": True,
            "verify_iss": True,
        },
    )
    sub = str(claims.get("sub") or "")
    if not sub.startswith("dev:") or not sub[4:].isdigit():
        raise ValueError("Malformed development subject")
    user_id = int(sub[4:])
    allowlist = allowed_user_ids()
    if allowlist and user_id not in allowlist:
        raise ValueError("User is not on the development allowlist")
    return claims


def dev_user_id_from_claims(claims: dict) -> int:
    return int(str(claims["sub"])[4:])


def _identity_rows(db: Session) -> list:
    """Seeded users available to the development roster (safe fields only)."""
    allowlist = allowed_user_ids()
    rows = db.execute(
        text(
            """
            SELECT u.id, u.first_name, u.last_name, u.email,
                   r.name AS role, d.name AS department
            FROM users u
            JOIN roles r ON r.id = u.role_id
            JOIN departments d ON d.id = u.department_id
            ORDER BY u.id
            """
        )
    ).mappings().all()
    out = []
    for row in rows:
        if allowlist and row["id"] not in allowlist:
            continue
        out.append(
            {
                "id": row["id"],
                "full_name": f"{row['first_name']} {row['last_name']}".strip(),
                "email": row["email"],
                "role": row["role"],
                "department": row["department"],
            }
        )
    return out


@config_router.get("/auth/config")
def auth_config(db: Session = Depends(get_db)) -> dict:
    """Public capability probe used by the UI to choose its sign-in path."""
    enabled = dev_auth_enabled()
    return {
        "mode": "development" if enabled else "supabase",
        "dev_auth": enabled,
        "production": current_environment() == "production",
        "token_ttl_seconds": TOKEN_TTL_SECONDS if enabled else None,
        "identities": _identity_rows(db) if enabled else [],
    }


@router.get("/dev-auth/identities")
def dev_identities(request: Request, db: Session = Depends(get_db)) -> list:
    """Persona roster for local development only."""
    _require_dev_request(request)
    return _identity_rows(db)


@router.post("/dev-auth/token")
def dev_token(payload: DevTokenRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    """Exchange a seeded user id for a short-lived, server-signed token."""
    _require_dev_request(request)
    allowlist = allowed_user_ids()
    if allowlist and payload.user_id not in allowlist:
        raise HTTPException(status_code=403, detail="User is not on the development allowlist")
    row = db.execute(
        text(
            """
            SELECT u.id, u.email, r.name AS role
            FROM users u JOIN roles r ON r.id = u.role_id
            WHERE u.id = :uid
            """
        ),
        {"uid": payload.user_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return issue_token(row["id"], row["email"], row["role"])
