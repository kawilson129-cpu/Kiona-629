"""Stage 1 verified-JWT to business-user resolution; no application wiring.

Configuration and lookup are supplied by trusted server code. No environment
loading, file/database writes, account creation, email matching, developer mode,
HTTP dependency, or unsigned identity-header fallback exists here.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Mapping

from auth import AuthenticationError, SupabaseJWTVerifier, extract_bearer_token
from rbac import Principal, Role, valid_id


class PrincipalResolutionError(Exception):
    """Verified identity lacks an authorized business mapping (future HTTP 403)."""


@dataclass(frozen=True)
class BusinessUser:
    """Snapshot read by a future trusted adapter; not an ORM model or seed row."""

    id: int
    role_id: int
    role_name: str
    department_id: int


class PrincipalResolver:
    def __init__(
        self, verifier: SupabaseJWTVerifier,
        subject_to_user: Mapping[str, int],
        load_user: Callable[[int], BusinessUser | None],
    ):
        mapping = dict(subject_to_user)
        if any(not isinstance(s, str) or not s.strip() or s != s.strip()
               or not valid_id(uid) for s, uid in mapping.items()):
            raise ValueError("Invalid subject mapping configuration")
        if len(set(mapping.values())) != len(mapping):
            raise ValueError("Subject mappings must be one-to-one")
        self._mapping = MappingProxyType(mapping)
        self._verifier = verifier
        self._load_user = load_user

    def resolve(self, authorization: str | None) -> Principal:
        # Do not catch verification failures or proceed to lookup on invalid tokens.
        claims = self._verifier.verify(extract_bearer_token(authorization))
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise AuthenticationError("Invalid token subject")
        user_id = self._mapping.get(subject)
        if user_id is None:
            raise PrincipalResolutionError("Identity is not linked to a business user")
        user = self._load_user(user_id)
        if (not isinstance(user, BusinessUser) or not valid_id(user.id)
                or user.id != user_id or not valid_id(user.role_id)
                or not valid_id(user.department_id)):
            raise PrincipalResolutionError("Business user is unavailable")
        try:
            role = Role(user.role_name)
        except (ValueError, TypeError):
            raise PrincipalResolutionError("Business role is not authorized") from None
        return Principal(subject, user.id, role, user.role_id, user.department_id)
