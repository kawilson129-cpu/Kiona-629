"""Week 7 — isolated tests for the Supabase JWT authentication foundation.

Fully offline: synthetic JWTs are signed with locally generated EC P-256 keys and
the JWKS response is mocked. No network, no database, no live Supabase, no auth
users, no application routes touched.

Run from backend/:
    python tests/test_week7_auth.py
"""

import base64
import json
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jwt
from cryptography.hazmat.primitives.asymmetric import ec

from auth import (
    AuthSettings,
    AuthenticationError,
    SupabaseJWTVerifier,
    extract_bearer_token,
    fetch_jwks,
)

PROJECT = "https://vnumvjamqtuxlctjdzoe.supabase.co"
ISSUER = f"{PROJECT}/auth/v1"
JWKS_URL = f"{PROJECT}/auth/v1/.well-known/jwks.json"
KID = "7400369a-63e5-40bf-b6d3-d49e126b0859"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _b64url_uint(value: int, size: int = 32) -> str:
    return base64.urlsafe_b64encode(value.to_bytes(size, "big")).rstrip(b"=").decode()


def _b64url_json(obj: dict) -> str:
    return base64.urlsafe_b64encode(
        json.dumps(obj, separators=(",", ":")).encode()
    ).rstrip(b"=").decode()


def make_ec_key():
    return ec.generate_private_key(ec.SECP256R1())


def make_jwks(key, kid=KID) -> dict:
    nums = key.public_key().public_numbers()
    return {
        "keys": [
            {
                "kty": "EC",
                "crv": "P-256",
                "use": "sig",
                "alg": "ES256",
                "kid": kid,
                "x": _b64url_uint(nums.x),
                "y": _b64url_uint(nums.y),
            }
        ]
    }


def build_token(
    key,
    kid=KID,
    *,
    iss=ISSUER,
    aud="authenticated",
    sub="11111111-2222-3333-4444-555555555555",
    iat_offset=0,
    exp_offset=3600,
    nbf_offset=None,
    alg="ES256",
    extra=None,
    omit=(),
) -> str:
    now = int(time.time())
    payload = {
        "iss": iss,
        "aud": aud,
        "sub": sub,
        "iat": now + iat_offset,
        "exp": now + exp_offset,
        "role": "authenticated",
        "email": "sam.okonkwo@aurumbank.com",
    }
    if nbf_offset is not None:
        payload["nbf"] = now + nbf_offset
    if extra:
        payload.update(extra)
    for claim in omit:
        payload.pop(claim, None)
    headers = {"kid": kid} if kid else None
    if alg == "none":
        header = {"alg": "none", "typ": "JWT"}
        if kid:
            header["kid"] = kid
        return f"{_b64url_json(header)}.{_b64url_json(payload)}."
    return jwt.encode(payload, key, algorithm=alg, headers=headers)


class FakeJWKClient:
    """Mimics PyJWKClient.get_signing_key_from_jwt against an in-memory JWKS."""

    def __init__(self, jwks: dict):
        self._jwks = jwks

    def get_signing_key_from_jwt(self, token: str):
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        for key in jwt.PyJWKSet.from_dict(self._jwks).keys:
            if key.key_id == kid:
                return key
        raise jwt.exceptions.PyJWKClientError(f"No matching key for kid={kid!r}")


def make_settings(**overrides) -> AuthSettings:
    base = dict(
        supabase_url=PROJECT,
        jwks_url=JWKS_URL,
        issuer=ISSUER,
        audience="authenticated",
        algorithms=("ES256",),
        leeway_seconds=0,
    )
    base.update(overrides)
    return AuthSettings(**base)


def make_verifier(jwks: dict, **setting_overrides) -> SupabaseJWTVerifier:
    return SupabaseJWTVerifier(make_settings(**setting_overrides), jwk_client=FakeJWKClient(jwks))


def expect_auth_error(fn, *args, **kwargs) -> str:
    try:
        fn(*args, **kwargs)
    except AuthenticationError as exc:
        return exc.message
    raise AssertionError("expected AuthenticationError, but none was raised")


# ---------------------------------------------------------------------------
# happy path
# ---------------------------------------------------------------------------
def test_valid_token_returns_claims():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    claims = verifier.verify(build_token(key))
    assert claims["sub"] == "11111111-2222-3333-4444-555555555555"
    assert claims["aud"] == "authenticated"
    assert claims["iss"] == ISSUER
    assert claims["role"] == "authenticated"


def test_audience_as_list_is_accepted():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    claims = verifier.verify(build_token(key, aud=["authenticated", "other"]))
    assert claims["aud"] == ["authenticated", "other"]


def test_leeway_allows_recent_expiry():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key), leeway_seconds=30)
    claims = verifier.verify(build_token(key, exp_offset=-5))
    assert claims["sub"]


# ---------------------------------------------------------------------------
# rejections
# ---------------------------------------------------------------------------
def test_missing_token_rejected():
    verifier = make_verifier(make_jwks(make_ec_key()))
    assert expect_auth_error(verifier.verify, None)
    assert expect_auth_error(verifier.verify, "")
    assert expect_auth_error(verifier.verify, "   ")


def test_malformed_token_rejected():
    verifier = make_verifier(make_jwks(make_ec_key()))
    assert expect_auth_error(verifier.verify, "not-a-jwt")


def test_expired_token_rejected():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    msg = expect_auth_error(verifier.verify, build_token(key, exp_offset=-10))
    assert "expired" in msg.lower()


def test_not_yet_valid_rejected():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    msg = expect_auth_error(verifier.verify, build_token(key, nbf_offset=3600))
    assert "not yet valid" in msg.lower()


def test_invalid_signature_rejected():
    real_key = make_ec_key()
    attacker_key = make_ec_key()
    verifier = make_verifier(make_jwks(real_key))
    msg = expect_auth_error(verifier.verify, build_token(attacker_key))
    assert "signature" in msg.lower()


def test_wrong_issuer_rejected():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    msg = expect_auth_error(verifier.verify, build_token(key, iss="https://evil.example/auth/v1"))
    assert "issuer" in msg.lower()


def test_wrong_audience_rejected():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    msg = expect_auth_error(verifier.verify, build_token(key, aud="service_role"))
    assert "audience" in msg.lower()


def test_unsupported_algorithm_hs256_rejected():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    hs_token = jwt.encode({"sub": "x", "iss": ISSUER, "aud": "authenticated", "exp": int(time.time()) + 60, "iat": int(time.time())},
                          "unit-test-only-hmac-key-0123456789abcdef", algorithm="HS256", headers={"kid": KID})
    msg = expect_auth_error(verifier.verify, hs_token)
    assert "algorithm" in msg.lower()


def test_unsupported_algorithm_none_rejected():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    msg = expect_auth_error(verifier.verify, build_token(key, alg="none"))
    assert "algorithm" in msg.lower()


def test_missing_required_claim_rejected():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    for claim in ("exp", "sub", "iat"):
        msg = expect_auth_error(verifier.verify, build_token(key, omit=(claim,)))
        assert "required claim" in msg.lower(), (claim, msg)


def test_unknown_kid_rejected():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    msg = expect_auth_error(verifier.verify, build_token(key, kid="no-such-key"))
    assert "signing key" in msg.lower()


# ---------------------------------------------------------------------------
# bearer parsing
# ---------------------------------------------------------------------------
def test_extract_bearer_token():
    assert extract_bearer_token("Bearer abc.def.ghi") == "abc.def.ghi"
    assert extract_bearer_token("bearer abc") == "abc"


def test_extract_bearer_token_rejects_bad_values():
    for value in (None, "", "abc", "Token abc", "Bearer", "Bearer a b"):
        expect_auth_error(extract_bearer_token, value)


# ---------------------------------------------------------------------------
# settings from env (no real secrets required)
# ---------------------------------------------------------------------------
def test_settings_from_env_defaults():
    s = AuthSettings.from_env({"SUPABASE_URL": PROJECT})
    assert s.jwks_url == JWKS_URL
    assert s.issuer == ISSUER
    assert s.audience == "authenticated"
    assert s.algorithms == ("ES256",)


def test_settings_from_env_overrides():
    s = AuthSettings.from_env(
        {
            "SUPABASE_URL": PROJECT + "/",
            "SUPABASE_JWKS_URL": "https://example.test/jwks.json",
            "SUPABASE_JWT_ISS": "https://example.test/auth/v1",
            "SUPABASE_JWT_AUD": "authenticated",
            "SUPABASE_JWT_ALGS": "ES256, RS256",
            "SUPABASE_JWT_LEEWAY": "15",
        }
    )
    assert s.supabase_url == PROJECT
    assert s.jwks_url == "https://example.test/jwks.json"
    assert s.algorithms == ("ES256", "RS256")
    assert s.leeway_seconds == 15


def test_settings_from_env_requires_url():
    expect_auth_error(AuthSettings.from_env, {})


# ---------------------------------------------------------------------------
# JWKS retrieval (mocked transport)
# ---------------------------------------------------------------------------
def test_fetch_jwks_ok():
    jwks = make_jwks(make_ec_key())
    got = fetch_jwks(make_settings(), http_get=lambda url, timeout: json.dumps(jwks).encode())
    assert got["keys"][0]["alg"] == "ES256"


def test_fetch_jwks_rejects_empty():
    msg = expect_auth_error(
        fetch_jwks, make_settings(), http_get=lambda url, timeout: b'{"keys": []}'
    )
    assert "no signing keys" in msg.lower()


def test_fetch_jwks_network_error_is_safe():
    def boom(url, timeout):
        raise OSError("connection refused")

    msg = expect_auth_error(fetch_jwks, make_settings(), http_get=boom)
    assert "unable to retrieve jwks" in msg.lower()


# ---------------------------------------------------------------------------
# no secret/token logging
# ---------------------------------------------------------------------------
class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def test_no_token_logged_on_failure():
    key = make_ec_key()
    verifier = make_verifier(make_jwks(key))
    token = build_token(make_ec_key())  # wrong key -> verification failure

    handler = _Capture()
    logger = logging.getLogger()
    logger.addHandler(handler)
    old_level = logger.level
    logger.setLevel(logging.DEBUG)
    try:
        expect_auth_error(verifier.verify, token)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(old_level)

    assert all(token not in m for m in handler.messages)
    assert all("shared-secret" not in m for m in handler.messages)


def test_auth_settings_have_no_secret_fields():
    settings = make_settings()
    fields = set(settings.__dataclass_fields__)
    for forbidden in ("secret", "password", "api_key", "service_key", "private_key"):
        assert not any(forbidden in f for f in fields)


if __name__ == "__main__":
    import traceback

    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
            traceback.print_exc()
    total = len(fns)
    print(f"\n{total - failed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
