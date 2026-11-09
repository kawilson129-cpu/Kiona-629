"""Isolated signed-identity control tests. Never loads production configuration."""
import json
import os
from pathlib import Path
import runpy
import socket
import sys
from time import perf_counter


def run(output):
    root = Path(__file__).resolve().parents[2]
    backend = root / "derexi-policy-pilot/backend"
    sys.path.insert(0, str(backend))

    # Disable dotenv and external network before loading the existing application.
    import dotenv
    dotenv.load_dotenv = lambda *args, **kwargs: False
    os.environ.update(DATABASE_URL="sqlite:///blocked-assessment.sqlite", DEREXI_ENV="test",
                      DEREXI_DEV_AUTH="1", DEREXI_DEV_USER_IDS="9001,9002")
    os.environ.pop("DEREXI_DEV_AUTH_SECRET", None)
    original_connect = socket.socket.connect

    def local_connect(sock, address):
        if isinstance(address, tuple) and address[0] in ("127.0.0.1", "::1"):
            return original_connect(sock, address)
        raise RuntimeError("External connections disabled in control suite")

    socket.socket.connect = local_connect
    socket.create_connection = lambda *args, **kwargs: (_ for _ in ()).throw(
        RuntimeError("External connections disabled in control suite"))
    # This harness installs Engine.connect tripwire before importing main.
    harness = runpy.run_path(str(backend / "tests/test_security_controls.py"))
    import main
    import dev_auth
    from pulse import service

    class Result:
        def __init__(self, row=None):
            self.row = row

        def mappings(self):
            return self

        def first(self):
            return self.row

    class Session(harness["FakeSession"]):
        def __init__(self, actor_role):
            super().__init__(rows={harness["Conversation"]: [harness["conversation"](1, 9001)],
                                   harness["Policy"]: [harness["policy"](1)],
                                   harness["PolicyVersion"]: [harness["version"](1)]})
            self.actor_role = actor_role

        def execute(self, statement, params=None):
            if "lower(u.email)" in str(statement):
                email = params["email"]
                uid = {"actor@example.invalid": 9001, "other@example.invalid": 9002}.get(email)
                return Result(dict(id=uid, email=email, first_name="Synthetic", last_name="Actor",
                                   department_id=1, role=self.actor_role) if uid else None)
            if "FROM clarification_requests cr" in str(statement):
                return Result()  # No thread assignment grants this actor access.
            return super().execute(statement, params)

    client = harness["CLIENT"]
    results = []

    def request(check_id, role, method, path, expected, *, payload=None, token="valid",
                uid=9001, group="access", impact=4, likelihood=3):
        session = Session(role)
        main.app.dependency_overrides[main.get_db] = lambda: session
        email = "actor@example.invalid" if uid == 9001 else "other@example.invalid"
        credential = dev_auth.issue_token(uid, email, role)["access_token"]
        headers = {} if token == "absent" else {"Authorization": "Bearer " + credential}
        if token == "tampered":
            headers["Authorization"] += "invalid"
        started = perf_counter()
        try:
            response = client.request(method, path, headers=headers, json=payload)
            passed = response.status_code == expected
            if expected >= 400:
                passed = passed and not session.added and session.committed == 0
            asset = "AUTH" if check_id.endswith(("IDENTITY", "SIGNATURE")) else "APP"
            results.append(dict(id=check_id, asset=asset, group=group, actor=role,
                                expected=expected, actual=response.status_code,
                                status="PASS" if passed else "FAIL", writes=len(session.added),
                                commits=session.committed, likelihood=likelihood, impact=impact,
                                elapsed_ms=round((perf_counter()-started)*1000, 3)))
        except Exception as exc:
            results.append(dict(id=check_id, asset="APP", group=group, status="ERROR",
                                error=type(exc).__name__, expected=expected))

    for role, short in [("Employee", "EMP"), ("Policy Owner", "OWN"), ("System Administrator", "ADM")]:
        request(short+"-IDENTITY", role, "GET", "/me", 200)
        request(short+"-SIGNATURE", role, "GET", "/me", 401, token="tampered")
        request(short+"-GOVERNANCE", role, "GET", "/dashboard/policy-health", 403 if short=="EMP" else 200)
        request(short+"-OWN", role, "GET", "/conversations/1", 200)
        request(short+"-OTHER", role, "GET", "/conversations/1", 200 if short=="ADM" else 404, uid=9002)
        request(short+"-BOOL", role, "POST", "/feedback", 422,
                payload=dict(message_id=1, rating="yes"), group="validation")
        request(short+"-LENGTH", role, "POST", "/feedback", 422,
                payload=dict(message_id=1, rating=True, comment="x"*50000), group="validation")
        request(short+"-APPROVE", role, "POST", "/policies", 201 if short=="ADM" else 403,
                payload=dict(title="Assessment policy", status="approved", version=dict(body="Synthetic")),
                group="policy-write", likelihood=4, impact=5)
    request("ANON-IDENTITY", "Employee", "GET", "/me", 401, token="absent")
    request("ANON-APPROVE", "Employee", "POST", "/policies", 401, token="absent",
            payload=dict(title="Assessment policy", status="approved", version=dict(body="Synthetic")),
            group="policy-write", likelihood=4, impact=5)
    request("EMP-VERSION", "Employee", "POST", "/policies/1/versions", 403,
            payload=dict(version_no="2.0", body="Synthetic revision"),
            group="policy-write", likelihood=4, impact=5)

    # Exercise shared middleware and a simulated database fault without disclosing internals.
    response = client.get("/")
    headers_ok = response.headers.get("X-Content-Type-Options") == "nosniff" and response.headers.get("X-Frame-Options") == "DENY"
    results.append(dict(id="HEADERS", asset="UI", group="headers", expected="nosniff and DENY",
                        actual={k: response.headers.get(k) for k in ("X-Content-Type-Options", "X-Frame-Options")},
                        status="PASS" if headers_ok else "FAIL", likelihood=2, impact=3))

    def broken_db():
        raise RuntimeError("SYNTHETIC_INTERNAL_MARKER")

    main.app.dependency_overrides[main.get_db] = broken_db
    response = client.get("/health")
    results.append(dict(id="SAFE-ERROR", asset="APP", group="errors", expected="500 without internal marker",
                        actual={"status":response.status_code,"body":response.text},
                        status="PASS" if response.status_code == 500 and "SYNTHETIC_INTERNAL_MARKER" not in response.text else "FAIL",
                        likelihood=2, impact=3))
    main.app.dependency_overrides.clear()
    article = service.make_article(source="FDIC", title="Synthetic notice",
                                   url="https://unrelated.example/notice", date="2026-11-09")
    results.append(dict(id="FEED-HOST", asset="PULSE", group="feed-integrity", expected="reject unrelated publisher host",
                        actual="accepted" if article else "rejected", status="FAIL" if article else "PASS",
                        likelihood=3, impact=4))
    Path(output).write_text(json.dumps(results, indent=2), encoding="utf-8")
    for row in results:
        print(row["id"], row["status"], "expected=", row["expected"], "actual=", row.get("actual", row.get("error")))
    return 2 if any(r["status"] == "ERROR" for r in results) else int(any(r["status"] == "FAIL" for r in results))


if __name__ == "__main__":
    sys.exit(run(sys.argv[1]))
