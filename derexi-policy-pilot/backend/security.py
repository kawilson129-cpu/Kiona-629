"""Server-side identity and authorization for DeRexi.

Two token issuers are supported, and only these two:

1. Supabase JWTs (production), verified against the project JWKS by
   ``auth.SupabaseJWTVerifier``.
2. Development tokens minted by ``dev_auth`` (local persona testing).

Both paths resolve the same ``public.users`` row and then apply the same
authorization rules. A caller's role is read from the database on every
request, so a stale token cannot retain elevated access after a role change.

The module also provides the SQL visibility predicate used by the messaging
read model. Backend connections use Supabase's ``postgres`` role, which
bypasses RLS, so these checks are the primary enforcement point; RLS policies
in ``backend/migrations`` provide defence in depth for direct Supabase clients.

No token, secret, or message body is ever logged here.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Optional, Tuple

import jwt
from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

import dev_auth
from database import get_db

ADMIN_ROLE = "System Administrator"
POLICY_OWNER_ROLE = "Policy Owner"
EMPLOYEE_ROLE = "Employee"
GOVERNANCE_ROLES = (ADMIN_ROLE, POLICY_OWNER_ROLE)
DEV_ALGORITHM = "HS256"
SUPABASE_FALLBACK_ALGORITHMS = ("ES256", "RS256")
_UNAUTHORIZED_HEADERS = {"WWW-Authenticate": "Bearer"}


@dataclass(frozen=True)
class Identity:
    """The authenticated actor, resolved from the database on each request."""

    user_id: int
    email: str
    full_name: str
    role: str
    department_id: Optional[int]
    token_source: str  # "supabase" or "dev"

    @property
    def is_admin(self) -> bool:
        return self.role == ADMIN_ROLE

    @property
    def is_policy_owner(self) -> bool:
        return self.role == POLICY_OWNER_ROLE

    @property
    def is_governance(self) -> bool:
        return self.role in GOVERNANCE_ROLES


def _unauthorized(message: str = "Invalid or missing credentials") -> HTTPException:
    # Deliberately generic: do not reveal whether a token existed, expired, or
    # named an unknown account.
    return HTTPException(status_code=401, detail=message, headers=_UNAUTHORIZED_HEADERS)


def extract_bearer(authorization: Optional[str]) -> str:
    if not authorization or not str(authorization).strip():
        raise _unauthorized("Authentication required")
    parts = str(authorization).split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise _unauthorized()
    return parts[1].strip()


_SUPABASE_VERIFIER = None


def _supabase_verifier():
    """Build (once) the Supabase verifier, or return None if not configured."""
    global _SUPABASE_VERIFIER
    if _SUPABASE_VERIFIER is not None:
        return _SUPABASE_VERIFIER
    try:
        from auth import AuthSettings, SupabaseJWTVerifier

        _SUPABASE_VERIFIER = SupabaseJWTVerifier(AuthSettings.from_env())
    except Exception:
        # Missing PyJWT, SUPABASE_URL, or JWKS configuration. The production
        # path is simply unavailable; dev auth (if enabled) still works.
        return None
    return _SUPABASE_VERIFIER


def verify_token(token: str) -> Tuple[dict, str]:
    """Return (claims, source) for a valid token, else 401."""
    try:
        header = jwt.get_unverified_header(token)
    except Exception:
        raise _unauthorized()
    alg = header.get("alg")

    if alg == DEV_ALGORITHM:
        if not dev_auth.dev_auth_enabled():
            raise _unauthorized()
        try:
            return dev_auth.verify_token(token), "dev"
        except Exception:
            raise _unauthorized()

    if alg in SUPABASE_FALLBACK_ALGORITHMS:
        verifier = _supabase_verifier()
        if verifier is None:
            raise _unauthorized()
        try:
            return verifier.verify(token), "supabase"
        except Exception:
            raise _unauthorized()

    raise _unauthorized()


def identity_from_user_row(row, source: str) -> Identity:
    return Identity(
        user_id=row["id"],
        email=row["email"],
        full_name=f"{row['first_name']} {row['last_name']}".strip(),
        role=row["role"],
        department_id=row.get("department_id"),
        token_source=source,
    )


def get_identity(
    request: Request,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> Identity:
    """FastAPI dependency: authenticate the bearer token and load the user."""
    token = extract_bearer(authorization) if authorization else request.cookies.get('derexi_access')
    if not token:
        raise _unauthorized('Authentication required')
    if not authorization and request.method not in {'GET', 'HEAD', 'OPTIONS'}:
        from session_auth import require_same_origin
        require_same_origin(request)
    claims, source = verify_token(token)
    if source == "dev":
        dev_auth._require_dev_request(request)

    return resolve_identity(request, claims, source, db)


def subject_bindings():
    try:
        bindings = json.loads(os.getenv('DEREXI_AUTH_SUBJECT_MAP', '{}'))
        if not isinstance(bindings, dict) or any(not isinstance(k, str) or not k
            or type(v) is not int or v <= 0 for k,v in bindings.items()):
            raise ValueError()
        return bindings
    except (ValueError, TypeError):
        raise HTTPException(503, 'Sign-in configuration is unavailable')


def resolve_identity(request, claims, source, db):
    email = str(claims.get("email") or "").strip().lower()
    if not email:
        raise _unauthorized()

    row = db.execute(
        text(
            """
            SELECT u.id, u.first_name, u.last_name, u.email, u.department_id,
                   r.name AS role
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE lower(u.email) = :email
            """
        ),
        {"email": email},
    ).mappings().first()
    if not row:
        raise _unauthorized()

    if source == 'supabase' and subject_bindings().get(claims.get('sub')) != row['id']:
        raise HTTPException(403, 'This account is not authorized for the workspace')
    if row['role'] not in {ADMIN_ROLE, POLICY_OWNER_ROLE, EMPLOYEE_ROLE}:
        raise HTTPException(403, 'Workspace access required')

    if source == "dev":
        # The token subject must match the resolved account; this blocks a
        # token for user A being replayed with user B's email claim.
        try:
            if dev_auth.dev_user_id_from_claims(claims) != row["id"]:
                raise _unauthorized()
        except Exception:
            raise _unauthorized()

    identity = identity_from_user_row(row, source)
    request.state.identity = identity
    return identity


def require_governance(identity: Identity = Depends(get_identity)) -> Identity:
    if not identity.is_governance:
        raise HTTPException(status_code=403, detail="Governance access required")
    return identity


def require_admin(identity: Identity = Depends(get_identity)) -> Identity:
    if not identity.is_admin:
        raise HTTPException(status_code=403, detail="Administrator access required")
    return identity


def require_owner_or_admin(identity: Identity = Depends(get_identity)) -> Identity:
    if not (identity.is_admin or identity.is_policy_owner):
        raise HTTPException(status_code=403, detail="Policy owner access required")
    return identity


def visibility_sql(identity: Identity, alias: str = "cr") -> Tuple[str, dict]:
    """SQL predicate limiting threads to those the identity may read.

    Administrators see the whole organisation (single-tenant Aurum deployment).
    Everyone else sees threads they requested, are assigned to, or have replied
    to. The predicate is always combined with an explicit ``user_id`` parameter
    so a caller cannot widen it.
    """
    if identity.is_admin:
        return "TRUE", {"scope_uid": identity.user_id}
    clause = (
        f"({alias}.user_id = :scope_uid OR {alias}.assigned_to = :scope_uid "
        f"OR EXISTS (SELECT 1 FROM clarification_replies pr "
        f"WHERE pr.request_id = {alias}.id AND pr.sender_id = :scope_uid))"
    )
    return clause, {"scope_uid": identity.user_id}


def can_access_thread(db: Session, identity: Identity, request_id: int) -> bool:
    clause, params = visibility_sql(identity, "cr")
    params["rid"] = request_id
    found = db.execute(
        text(f"SELECT 1 FROM clarification_requests cr WHERE cr.id = :rid AND ({clause})"),
        params,
    ).first()
    return found is not None


def assert_thread_access(db: Session, identity: Identity, request_id: int) -> None:
    """404 (not 403) for a thread the caller may not see, to avoid ID probing."""
    if not can_access_thread(db, identity, request_id):
        raise HTTPException(status_code=404, detail="Clarification request not found")
