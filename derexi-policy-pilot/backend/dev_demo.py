"""Explicit loopback demo over an ephemeral copy of an approved SQLite file.

No seed/import/export of course records is performed. Production never imports
this entry point or accepts its per-process signing key, issuer or sessions.
"""
from __future__ import annotations

import argparse
import ipaddress
import secrets
import sqlite3
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, urlsplit

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import Field
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text

import main
import models as m
from auth import AuthSettings, SupabaseJWTVerifier
from rbac import Role
from schemas import RequestModel, RecordId
from secure_api import create_app

COOKIE = "derexi_local_session"


class Activation(RequestModel):
    key: str = Field(min_length=1, max_length=512)


class Selection(RequestModel):
    user_id: RecordId


@dataclass(frozen=True)
class LocalSession:
    token: str
    user_id: int
    csrf: str
    deadline: float


def build_demo(database_path, origin="http://127.0.0.1:8000"):
    parts = urlsplit(origin)
    if parts.scheme != "http" or parts.hostname != "127.0.0.1" or parts.path or parts.query or parts.fragment or parts.username:
        raise ValueError("Use a loopback http://127.0.0.1 origin")
    path = Path(database_path).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError("Supply an approved local SQLite snapshot")
    runtime = tempfile.TemporaryDirectory(prefix="derexi-local-demo-")
    target = Path(runtime.name) / "demo.sqlite"
    # Source is read-only; all demo writes go to a disposable per-process copy.
    with sqlite3.connect("file:" + quote(str(path)) + "?mode=ro", uri=True) as source:
        with sqlite3.connect(target) as destination:
            source.backup(destination)
    engine = create_engine("sqlite+pysqlite:///" + str(target), connect_args={"check_same_thread": False})
    @event.listens_for(engine, "connect")
    def local_constraints(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")
    class DemoSession(Session):
        def execute(self, statement, params=None, **kwargs):
            # SQLite has no pg_trgm. Keep this explicitly local lexical adapter
            # separate from the unchanged production query and thresholds.
            if statement is main.SEARCH_SQL:
                terms = main.substantive_keywords((params or {}).get("q", ""))
                values = {"limit": (params or {}).get("limit", 5)}
                for i, word in enumerate(terms):
                    values["term" + str(i)] = "%" + word + "%"
                def hits(column):
                    return " + ".join(f"CASE WHEN lower({column}) LIKE :term{i} THEN 1.0 ELSE 0 END" for i in range(len(terms))) or "0.0"
                score = f"(0.6 * ({hits('cv.body')}) + 0.4 * ({hits('cv.title')})) / {max(1, len(terms))}"
                query = text(f"""WITH cv AS (
                    SELECT pv.*, row_number() OVER (PARTITION BY policy_id ORDER BY created_at DESC, id DESC) AS rn
                    FROM policy_versions pv)
                    SELECT p.id AS policy_id, p.title, p.summary, cv.id AS policy_version_id,
                           cv.version_no, cv.body, {score} AS score
                    FROM cv JOIN policies p ON p.id=cv.policy_id
                    WHERE cv.rn=1 AND p.status='approved' ORDER BY score DESC, p.id LIMIT :limit""")
                return super().execute(query, values, **kwargs)
            return super().execute(statement, params, **kwargs)
    factory = sessionmaker(bind=engine, class_=DemoSession, autoflush=False, expire_on_commit=False)
    with factory() as db:
        users = db.query(m.User).all()
        eligible = [u for u in users if u.role is not None and u.role.name in {r.value for r in Role}]
        if not eligible:
            raise ValueError("The snapshot has no supported business users; no users were created")
        mapping = {"local-" + str(u.id): u.id for u in eligible}
        employees = [u.id for u in eligible if u.role.name == Role.EMPLOYEE.value]
        initial_id = min(employees or [u.id for u in eligible])

    # A fresh asymmetric key and unique issuer cannot authenticate to production.
    signing_key = ec.generate_private_key(ec.SECP256R1())
    issuer = "urn:derexi:local:" + secrets.token_hex(16)
    class LocalKeys:
        def get_signing_key_from_jwt(self, token):
            return signing_key.public_key()
    verifier = SupabaseJWTVerifier(AuthSettings(origin, origin + "/unused-jwks", issuer,
                                               audience="derexi-local-only"), jwk_client=LocalKeys())
    app = create_app(verifier, mapping)
    app.state.runtime = runtime
    app.state.local_engine = engine
    def local_db():
        with factory() as db:
            yield db
    app.dependency_overrides[main.get_db] = local_db
    # Never send copied demo questions/context to a configured live AI provider.
    app.dependency_overrides[main.answer_generator] = lambda: (lambda q, context: None)
    sessions = {}
    bootstrap = secrets.token_urlsafe(32)
    activation_deadline = time.monotonic() + 300
    key_path = Path(runtime.name) / "activation-key"
    key_path.touch(mode=0o600, exist_ok=False)
    key_path.write_text(bootstrap)
    app.state.activation_key_path = key_path

    def issue(uid):
        now = int(time.time())
        token = jwt.encode({"sub": "local-" + str(uid), "iss": issuer,
                            "aud": "derexi-local-only", "iat": now, "exp": now + 3600},
                           signing_key, algorithm="ES256", headers={"kid": "local"})
        sid = secrets.token_urlsafe(32)
        session = LocalSession(token, uid, secrets.token_urlsafe(32), time.monotonic() + 3600)
        # The local developer has one active session; rotation revokes old IDs.
        sessions.clear()
        sessions[sid] = session
        response = JSONResponse({"user_id": uid, "csrf": session.csrf})
        response.set_cookie(COOKIE, sid, httponly=True, samesite="strict", max_age=3600, path="/")
        return response

    @app.middleware("http")
    async def loopback_session(request: Request, call_next):
        try:
            local = request.client is not None and ipaddress.ip_address(request.client.host).is_loopback
        except ValueError:
            local = False
        if not local or request.headers.get("host") != parts.netloc:
            return JSONResponse({"detail": "Local demo access only"}, status_code=403)
        if request.method not in ("GET", "HEAD") and request.headers.get("origin") != origin:
            return JSONResponse({"detail": "Same-origin request required"}, status_code=403)
        public = request.url.path in ("/__dev/login", "/__dev/login.js")
        if not public:
            session = sessions.get(request.cookies.get(COOKIE))
            if session is None or session.deadline <= time.monotonic():
                if request.method == "GET" and request.url.path.startswith("/ui"):
                    return RedirectResponse("/__dev/login")
                return JSONResponse({"detail": "Activate a local developer session"}, status_code=401)
            if request.method not in ("GET", "HEAD") and not secrets.compare_digest(
                    request.headers.get("x-csrf-token", ""), session.csrf):
                return JSONResponse({"detail": "Invalid request verification token"}, status_code=403)
            request.state.local_session = session
            # The cookie session chooses the signed identity; caller headers do not.
            request.scope["headers"] = [(k, v) for k, v in request.scope["headers"] if k.lower() != b"authorization"]
            request.scope["headers"].append((b"authorization", ("Bearer " + session.token).encode()))
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; frame-ancestors 'none'; base-uri 'none'"
        return response

    @app.get("/__dev/login", response_class=HTMLResponse)
    def login_page():
        return '<!doctype html><title>Activate DeRexi local demo</title><h1>Local developer demo</h1><form><label>One-time activation key <input id="key" type="password" autocomplete="off" required></label><button>Activate</button></form><p id="error"></p><script src="/__dev/login.js"></script>'

    @app.get("/__dev/login.js")
    def login_script():
        return PlainTextResponse("document.querySelector('form').onsubmit=async function(e){e.preventDefault();var r=await fetch('/__dev/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:document.querySelector('#key').value})});if(r.ok)location.replace('/ui/');else document.querySelector('#error').textContent='Activation failed or expired. Restart the local demo to try again.';};", media_type="application/javascript")

    @app.post("/__dev/login")
    def activate(payload: Activation):
        nonlocal bootstrap
        if time.monotonic() > activation_deadline or not bootstrap or not secrets.compare_digest(payload.key, bootstrap):
            raise HTTPException(401, "Invalid or expired activation")
        bootstrap = ""
        key_path.unlink(missing_ok=True)
        return issue(initial_id)

    @app.get("/__dev/session")
    def session_info(request: Request):
        session = request.state.local_session
        return {"user_id": session.user_id, "csrf": session.csrf}

    @app.post("/__dev/switch")
    def switch(payload: Selection):
        # Recheck the copied roster; switching never edits role/department rows.
        with factory() as db:
            user = db.get(m.User, payload.user_id)
            if user is None or user.role is None or user.role.name not in {r.value for r in Role}:
                raise HTTPException(403, "Unknown local identity")
        return issue(payload.user_id)

    @app.post("/__dev/logout")
    def logout():
        sessions.clear()
        response = JSONResponse({"status": "signed out"})
        response.delete_cookie(COOKIE)
        return response

    @app.get("/__dev/bridge.js")
    def bridge():
        return PlainTextResponse((Path(__file__).parent / "dev_bridge.js").read_text(), media_type="application/javascript")

    @app.get("/ui/", response_class=HTMLResponse)
    def employee_ui():
        html = (main.STATIC_DIR / "index.html").read_text()
        return html.replace("</head>", '<script src="/__dev/bridge.js"></script></head>')
    app.mount("/ui", StaticFiles(directory=main.STATIC_DIR, html=True), name="demo-ui")
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start an explicitly activated, isolated local demo")
    parser.add_argument("--database", required=True, help="Approved existing local SQLite snapshot")
    parser.add_argument("--activate", action="store_true", required=True)
    parser.add_argument("--port", type=int, default=8000)
    options = parser.parse_args()
    app = build_demo(options.database, "http://127.0.0.1:" + str(options.port))
    print("Read the one-time key from this local protected file:", app.state.activation_key_path)
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=options.port, proxy_headers=False)
