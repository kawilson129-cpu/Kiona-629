"""Isolated Supabase JWT authentication foundation for DeRexi.

This module is deliberately **not imported by the running application**. It is the
Week 7 authentication foundation: a reusable verifier that validates Supabase-issued
JWTs against the project's published JWKS. Nothing here changes existing routes,
creates auth users, touches the database, or alters Row Level Security.

Verification performed:
  * signature, using the public key resolved from the Supabase JWKS endpoint
  * allowed algorithm (ES256 only by default)
  * expiration (``exp``) and not-before (``nbf``) with optional leeway
  * issuer (``iss``)
  * audience (``aud``)
  * required claims (``exp``, ``iat``, ``sub``, ``aud``, ``iss``)

Rejected: missing tokens, expired tokens, invalid signatures, incorrect issuer,
incorrect audience, unsupported algorithms, malformed tokens, unknown key ids.

No token or secret value is ever logged.

Example (future wiring -- do NOT add to routes without approval):

    from auth import SupabaseJWTVerifier, AuthSettings, extract_bearer_token

    verifier = SupabaseJWTVerifier(AuthSettings.from_env())

    @app.get("/me")
    def me(authorization: str | None = Header(default=None)):
        claims = verifier.verify(extract_bearer_token(authorization))
        ...
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Protocol, Sequence, Tuple

import jwt
from jwt import PyJWKClient
from jwt.exceptions import (
    ExpiredSignatureError,
    ImmatureSignatureError,
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
    PyJWKClientError,
)

__all__ = [
    "AuthenticationError",
    "AuthSettings",
    "SupabaseJWTVerifier",
    "extract_bearer_token",
    "fetch_jwks",
    "build_bearer_claims_dependency",
]

DEFAULT_AUDIENCE = "authenticated"
DEFAULT_ALGORITHMS: Tuple[str, ...] = ("ES256",)
REQUIRED_CLAIMS: Tuple[str, ...] = ("exp", "iat", "sub", "aud", "iss")
DEFAULT_TIMEOUT_SECONDS = 5.0
DEFAULT_JWKS_PATH = "/auth/v1/.well-known/jwks.json"


class AuthenticationError(Exception):
    """A missing or invalid bearer token (maps to HTTP 401)."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass(frozen=True)
class AuthSettings:
    """Resolved Supabase auth configuration (no secrets: only public values)."""

    supabase_url: str
    jwks_url: str
    issuer: str
    audience: str = DEFAULT_AUDIENCE
    algorithms: Tuple[str, ...] = DEFAULT_ALGORITHMS
    leeway_seconds: int = 0
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls, env: Optional[dict] = None) -> "AuthSettings":
        env = os.environ if env is None else env
        supabase_url = (env.get("SUPABASE_URL") or "").strip().rstrip("/")
        if not supabase_url:
            raise AuthenticationError(
                "SUPABASE_URL is not configured (needed to locate the JWKS endpoint)"
            )
        jwks_url = (env.get("SUPABASE_JWKS_URL") or f"{supabase_url}{DEFAULT_JWKS_PATH}").strip()
        issuer = (env.get("SUPABASE_JWT_ISS") or f"{supabase_url}/auth/v1").strip()
        audience = (env.get("SUPABASE_JWT_AUD") or DEFAULT_AUDIENCE).strip()

        raw_algs = env.get("SUPABASE_JWT_ALGS") or ",".join(DEFAULT_ALGORITHMS)
        algorithms = tuple(a.strip() for a in str(raw_algs).split(",") if a.strip())
        if not algorithms:
            algorithms = DEFAULT_ALGORITHMS

        try:
            leeway = int(env.get("SUPABASE_JWT_LEEWAY") or 0)
        except (TypeError, ValueError):
            leeway = 0
        try:
            timeout = float(env.get("SUPABASE_JWKS_TIMEOUT") or DEFAULT_TIMEOUT_SECONDS)
        except (TypeError, ValueError):
            timeout = DEFAULT_TIMEOUT_SECONDS

        return cls(
            supabase_url=supabase_url,
            jwks_url=jwks_url,
            issuer=issuer,
            audience=audience,
            algorithms=algorithms,
            leeway_seconds=leeway,
            timeout_seconds=timeout,
        )


class SigningKeyResolver(Protocol):
    """Anything that can resolve a token's signing key (PyJWKClient-compatible)."""

    def get_signing_key_from_jwt(self, token: str) -> Any:  # pragma: no cover - protocol
        ...


def _default_http_get(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as resp:  # noqa: S310 (fixed https URL)
        return resp.read()


def fetch_jwks(
    settings: AuthSettings,
    http_get: Optional[Callable[[str, float], bytes]] = None,
) -> dict:
    """Read-only fetch of the project's public JWKS (no secrets involved).

    ``http_get`` is injectable so tests never hit the network.
    """
    getter = http_get or _default_http_get
    try:
        raw = getter(settings.jwks_url, settings.timeout_seconds)
    except AuthenticationError:
        raise
    except Exception as exc:  # noqa: BLE001 - surface a single safe error type
        raise AuthenticationError("Unable to retrieve JWKS from Supabase") from exc

    try:
        payload = json.loads(raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw)
    except (ValueError, AttributeError) as exc:
        raise AuthenticationError("JWKS response was not valid JSON") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list) or not payload["keys"]:
        raise AuthenticationError("JWKS response contained no signing keys")
    return payload


def extract_bearer_token(authorization: Optional[str]) -> str:
    """Pull the token out of an ``Authorization: Bearer <token>`` header value."""
    if not authorization or not str(authorization).strip():
        raise AuthenticationError("Missing Authorization header")
    parts = str(authorization).split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise AuthenticationError("Malformed Authorization header (expected 'Bearer <token>')")
    return parts[1].strip()


class SupabaseJWTVerifier:
    """Validates Supabase-issued JWTs against the project JWKS."""

    def __init__(
        self,
        settings: AuthSettings,
        jwk_client: Optional[SigningKeyResolver] = None,
    ):
        self._settings = settings
        self._algorithms = tuple(settings.algorithms)
        self._jwk_client = jwk_client if jwk_client is not None else self._build_jwk_client(settings)

    @staticmethod
    def _build_jwk_client(settings: AuthSettings) -> PyJWKClient:
        # cache_keys caches by kid; timeout bounds the network call. Some PyJWT
        # versions do not accept ``timeout`` -- fall back if so.
        try:
            return PyJWKClient(
                settings.jwks_url,
                cache_keys=True,
                lifespan=300,
                timeout=settings.timeout_seconds,
            )
        except TypeError:  # pragma: no cover - only for older PyJWT
            return PyJWKClient(settings.jwks_url, cache_keys=True)

    @property
    def settings(self) -> AuthSettings:
        return self._settings

    def _resolve_key(self, token: str) -> Any:
        try:
            signing_key = self._jwk_client.get_signing_key_from_jwt(token)
        except PyJWKClientError as exc:
            raise AuthenticationError("Unable to resolve a signing key for the token") from exc
        except Exception as exc:  # noqa: BLE001
            raise AuthenticationError("Unable to resolve a signing key for the token") from exc
        return getattr(signing_key, "key", signing_key)

    def verify(self, token: Optional[str]) -> dict:
        """Return verified claims, or raise :class:`AuthenticationError`."""
        if not token or not str(token).strip():
            raise AuthenticationError("Missing bearer token")
        token = str(token).strip()

        # 1. Reject unsupported algorithms before touching keys (defense in depth
        #    against algorithm-confusion / 'none' attacks).
        try:
            header = jwt.get_unverified_header(token)
        except InvalidTokenError as exc:
            raise AuthenticationError("Malformed token") from exc
        alg = header.get("alg")
        if alg not in self._algorithms:
            raise AuthenticationError(f"Unsupported token algorithm: {alg!r}")

        # 2. Resolve the public signing key from JWKS.
        key = self._resolve_key(token)

        # 3. Full verification.
        try:
            claims = jwt.decode(
                token,
                key,
                algorithms=list(self._algorithms),
                audience=self._settings.audience,
                issuer=self._settings.issuer,
                leeway=self._settings.leeway_seconds,
                options={
                    "require": list(REQUIRED_CLAIMS),
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )
        except ExpiredSignatureError as exc:
            raise AuthenticationError("Token has expired") from exc
        except ImmatureSignatureError as exc:
            raise AuthenticationError("Token is not yet valid") from exc
        except InvalidAudienceError as exc:
            raise AuthenticationError("Token audience is invalid") from exc
        except InvalidIssuerError as exc:
            raise AuthenticationError("Token issuer is invalid") from exc
        except InvalidAlgorithmError as exc:
            raise AuthenticationError("Unsupported token algorithm") from exc
        except InvalidSignatureError as exc:
            raise AuthenticationError("Token signature is invalid") from exc
        except MissingRequiredClaimError as exc:
            raise AuthenticationError(f"Token is missing a required claim: {exc.claim}") from exc
        except InvalidTokenError as exc:
            raise AuthenticationError("Invalid token") from exc

        return claims


def build_bearer_claims_dependency(verifier: SupabaseJWTVerifier):
    """Build (but do not register) a FastAPI dependency returning verified claims.

    Provided for future, approved wiring only. Importing FastAPI lazily keeps this
    module usable in plain unit tests.
    """
    from fastapi import Header, HTTPException  # local import: optional dependency

    def _dependency(authorization: Optional[str] = Header(default=None)) -> dict:
        try:
            return verifier.verify(extract_bearer_token(authorization))
        except AuthenticationError as exc:
            raise HTTPException(
                status_code=401,
                detail=exc.message,
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    return _dependency
