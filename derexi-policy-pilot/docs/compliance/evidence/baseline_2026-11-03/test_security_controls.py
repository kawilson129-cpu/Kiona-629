"""Compliance 1 Assignment 1 — isolated verification of controls C-01 and C-02.

C-01  Role-based access control (Employee / Policy Owner / System Administrator)
C-02  Input validation and safe error handling

SAFETY MODEL
------------
* No live database is contacted. ``get_db`` is overridden per test with an
  in-memory fake session that records writes instead of performing them.
* ``Engine.connect`` is replaced with a tripwire that raises, so any accidental
  path to the real Supabase database fails loudly instead of reading or writing.
* No production users, permissions, records, RLS policies, or schema are
  touched. Identities used below are synthetic (``*.example.invalid``).

Each check asserts the behaviour the control *requires*. A FAIL therefore means
the application does not currently meet that requirement; the same suite can be
re-run unchanged after remediation.

Run from backend/:
    python tests/test_security_controls.py
"""

import json
import os
import re
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tripwire: created before the app is imported so no code path can open a real
# connection. This is a test-process-only patch.
from sqlalchemy.engine import Engine


def _blocked_connect(self, *args, **kwargs):  # noqa: ANN001
    raise RuntimeError("Live database access attempted during an isolated test")


Engine.connect = _blocked_connect

import main  # noqa: E402
import schemas  # noqa: E402
from fastapi.routing import APIRoute  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from models import (  # noqa: E402
    ClarificationReply,
    ClarificationRequest,
    Conversation,
    Feedback,
    IncidentCategory,
    IncidentReport,
    Message,
    Policy,
    PolicyVersion,
    Role,
    User,
)
from sqlalchemy.sql import operators  # noqa: E402

RESULTS = []
APPENDIX = {"routes": [], "cors_allow_origins": [], "auth_module_imported": False}
CURRENT_TEST = ""


def check(test_id, control, scenario, expected, passed, actual):
    """Record one executed check; print a single readable line."""
    RESULTS.append({
        "id": test_id,
        "control": control,
        "scenario": scenario,
        "expected": expected,
        "actual": actual,
        "status": "PASS" if passed else "FAIL",
        "function": CURRENT_TEST,
    })
    print(("  PASS  " if passed else "  FAIL  ") + test_id + "  " + scenario)
    if not passed:
        print("        expected: " + expected)
        print("        actual:   " + actual)


def blocked(test_id, control, scenario, expected, reason):
    RESULTS.append({
        "id": test_id,
        "control": control,
        "scenario": scenario,
        "expected": expected,
        "actual": reason,
        "status": "BLOCKED",
    })
    print("  BLOCK  " + test_id + "  " + scenario + " — " + reason)


# ---------------------------------------------------------------------------
# In-memory fake session
# ---------------------------------------------------------------------------
def _col_name(expr):
    left = getattr(expr, "left", None)
    return getattr(left, "key", None) or getattr(left, "name", None)


def _col_value(expr):
    right = expr.right
    while hasattr(right, "value") and not isinstance(right, str):
        right = right.value
    return right


class FakeQuery:
    def __init__(self, rows):
        self._rows = list(rows)
        self._filters = []

    def filter(self, *criteria):
        self._filters.extend(criteria)
        return self

    def order_by(self, *args):
        return self

    def first(self):
        rows = self.all()
        return rows[0] if rows else None

    def all(self):
        out = self._rows
        for expr in self._filters:
            col = _col_name(expr)
            try:
                value = _col_value(expr)
            except Exception:  # noqa: BLE001 - unsupported expression, keep rows
                continue
            if expr.operator is operators.eq and col:
                out = [r for r in out if getattr(r, col, None) == value]
        return out


class FakeResult:
    def __init__(self, rows=None, one=None, scalar=None):
        self._rows = list(rows or [])
        self._one = one
        self._scalar = scalar

    def mappings(self):
        return self

    def all(self):
        return self._rows

    def one(self):
        return self._one if self._one is not None else {}

    def scalar(self):
        return self._scalar


def _stamp(obj):
    if getattr(obj, "created_at", None) is None:
        obj.created_at = main.datetime(2026, 1, 1, 12, 0, 0)
    if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
        obj.updated_at = main.datetime(2026, 1, 1, 12, 0, 0)


class FakeSession:
    """Records writes; never opens a connection."""

    def __init__(self, rows=None):
        self.rows = {k: list(v) for k, v in (rows or {}).items()}
        self.added = []
        self.committed = 0
        self.flushed = 0
        self._next_id = 5000

    # -- reads ------------------------------------------------------------
    def get(self, model, pk):
        pool = self.rows.get(model, []) + [a for a in self.added if isinstance(a, model)]
        return next((r for r in pool if getattr(r, "id", None) == pk), None)

    def query(self, model):
        pool = self.rows.get(model, []) + [a for a in self.added if isinstance(a, model)]
        return FakeQuery(pool)

    def execute(self, stmt, params=None):
        sql = " ".join(str(stmt).lower().split())

        if "word_similarity" in sql:
            return FakeResult(rows=self.search_rows)

        if "owner_id from policies" in sql or "where r.name = 'policy owner'" in sql:
            return FakeResult(scalar=9)

        if "group by status" in sql:
            return FakeResult(rows=[])
        if "review_date" in sql and "count(*) as count" in sql:
            return FakeResult(scalar=0)
        if "from feedback" in sql:
            return FakeResult(one={"total": 0, "helpful": 0, "not_helpful": 0})
        if "policy_citations" in sql:
            return FakeResult(rows=[])
        if "select (select count(*)" in sql:
            return FakeResult(one={"policies": 0, "conversations": 0,
                                   "messages": 0, "incidents": 0})
        return FakeResult(rows=[])

    # -- writes -----------------------------------------------------------
    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self._next_id
            self._next_id += 1
        _stamp(obj)
        self.added.append(obj)

    def flush(self):
        self.flushed += 1

    def commit(self):
        self.committed += 1

    def refresh(self, obj):
        return None

    def close(self):
        return None

    @property
    def search_rows(self):
        return getattr(self, "_search_rows", [])


APP = main.app
CLIENT = TestClient(APP, raise_server_exceptions=False)


def reset(**kwargs):
    """Install a fresh fake session for one test; returns it."""
    session = FakeSession(rows=kwargs.get("rows"))
    session._search_rows = kwargs.get("search_rows", [])
    APP.dependency_overrides[main.get_db] = lambda: session
    return session


def teardown():
    APP.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Synthetic fixtures (no real users or records)
# ---------------------------------------------------------------------------
def user(uid, role_id=1):
    u = User()
    u.id = uid
    u.first_name = "Demo"
    u.last_name = "User%d" % uid
    u.email = "user%d@example.invalid" % uid
    u.department_id = 1
    u.role_id = role_id
    u.department = None
    u.role = None
    return u


def role(rid, name):
    r = Role()
    r.id = rid
    r.name = name
    return r


def incident(iid, reporter=8, status="reported"):
    i = IncidentReport()
    i.id = iid
    i.reporter_id = reporter
    i.category_id = None
    i.description = "Synthetic test record"
    i.severity = "medium"
    i.status = status
    i.assigned_to = None
    i.escalation_level = 1
    i.resolution_notes = None
    i.reporter = None
    i.category = None
    i.assignee = None
    return i


def clarification(rid, requester=8, assignee=9):
    c = ClarificationRequest()
    c.id = rid
    c.user_id = requester
    c.message_id = None
    c.conversation_id = None
    c.policy_id = None
    c.reason = "Synthetic question"
    c.status = "open"
    c.assigned_to = assignee
    c.resolved_at = None
    c.requester = None
    c.assignee = None
    return c


def conversation(cid, owner=8):
    conv = Conversation()
    conv.id = cid
    conv.user_id = owner
    conv.topic = "Synthetic conversation"
    conv.status = "open"
    conv.messages = []
    return conv


def policy(pid=1):
    p = Policy()
    p.id = pid
    p.title = "Synthetic Policy"
    p.summary = None
    p.status = "approved"
    p.category_id = None
    p.owner_id = None
    p.category = None
    p.owner = None
    p.created_at = main.datetime(2026, 1, 1)
    p.updated_at = main.datetime(2026, 1, 1)
    return p


def version(pid=1):
    v = PolicyVersion()
    v.id = 77
    v.policy_id = pid
    v.version_no = "1.0"
    v.title = "Synthetic Policy"
    v.body = "Synthetic policy body for test purposes only."
    v.effective_date = None
    v.review_date = None
    v.requires_review = False
    v.created_by = None
    return v


# ===========================================================================
# C-01 — Role-based access control
# ===========================================================================
PROTECTED_ROUTES = [
    ("GET", "/users"),
    ("POST", "/policies"),
    ("POST", "/policies/1/versions"),
    ("PATCH", "/incidents/1"),
    ("GET", "/incidents"),
    ("GET", "/clarifications"),
    ("POST", "/clarifications/1/replies"),
    ("POST", "/clarifications/1/resolve"),
    ("GET", "/conversations/1"),
    ("GET", "/dashboard/policy-health"),
]


def _route_has_identity_dependency(route):
    """True when a route declares an auth/role dependency (not just get_db)."""
    if not isinstance(route, APIRoute):
        return False
    for dep in route.dependant.dependencies:
        call = dep.call
        name = (getattr(call, "__name__", "") or "").lower()
        module = (getattr(call, "__module__", "") or "").lower()
        if any(k in name for k in ("auth", "current_user", "require", "permission", "verify")):
            return True
        if "auth" in module:
            return True
    return False


def test_c01_01_no_authorization_dependencies():
    """Every protected route should declare an identity/permission dependency."""
    unprotected = []
    for route in APP.routes:
        if not isinstance(route, APIRoute):
            continue
        methods = sorted(m for m in route.methods if m not in ("HEAD", "OPTIONS"))
        public = route.path in ("/", "/health") or route.path.startswith(
            ("/api/pulse", "/ui", "/docs", "/redoc", "/openapi"))
        protected = _route_has_identity_dependency(route)
        APPENDIX["routes"].append({
            "methods": methods,
            "path": route.path,
            "public_by_design": public,
            "authorization_dependency": protected,
        })
        if public:
            continue
        if not protected:
            unprotected.append("%s %s" % ("/".join(methods), route.path))

    check(
        "C01-01", "C-01",
        "Every API route declares an identity/role dependency",
        "0 routes without an authorization dependency",
        len(unprotected) == 0,
        "%d route(s) unprotected: %s" % (len(unprotected), ", ".join(unprotected)),
    )


def test_c01_02_auth_module_not_wired():
    """The JWT verifier exists but must be used by the application to enforce roles."""
    source = open(os.path.join(os.path.dirname(__file__), "..", "main.py"), encoding="utf-8").read()
    wired = bool(re.search(r"^\s*(from\s+auth\s+import|import\s+auth\b)", source, re.M))
    APPENDIX["auth_module_imported"] = wired
    check(
        "C01-02", "C-01",
        "Auth foundation (auth.py) is imported and used by main.py",
        "main.py imports and enforces auth",
        wired,
        "main.py has no import of auth.py; the verifier is unwired",
    )


def test_c01_03_anonymous_user_directory():
    reset(rows={User: [user(8, 1)], Role: [role(1, "Employee")]})
    r = CLIENT.get("/users")
    body = r.text
    check(
        "C01-03", "C-01",
        "Anonymous GET /users is denied",
        "401/403 and no user data",
        r.status_code in (401, 403),
        "HTTP %d; returned %d user record(s)%s"
        % (r.status_code, len(r.json()) if r.status_code == 200 else 0,
           " including email addresses" if "@" in body else ""),
    )


def test_c01_04_anonymous_incidents():
    reset(rows={IncidentReport: [incident(1, reporter=8)]})
    r = CLIENT.get("/incidents")
    exposed = r.status_code == 200 and any(
        item.get("description") for item in r.json()
    )
    check(
        "C01-04", "C-01",
        "Anonymous GET /incidents is denied",
        "401/403 and no incident data",
        r.status_code in (401, 403),
        "HTTP %d%s" % (r.status_code, "; incident description exposed" if exposed else ""),
    )


def test_c01_05_anonymous_clarifications():
    reset(rows={ClarificationRequest: [clarification(1)]})
    r = CLIENT.get("/clarifications")
    check(
        "C01-05", "C-01",
        "Anonymous GET /clarifications is denied",
        "401/403 and no thread data",
        r.status_code in (401, 403),
        "HTTP %d%s" % (r.status_code, "; %d thread(s) returned" % len(r.json())
                       if r.status_code == 200 else ""),
    )


def test_c01_06_cross_user_conversation_read():
    reset(rows={Conversation: [conversation(1, owner=8)]})
    # There is no credential mechanism, so identity is only asserted by a header.
    r = CLIENT.get("/conversations/1", headers={"X-Demo-User-Id": "9"})
    check(
        "C01-06", "C-01",
        "User 9 cannot read user 8's conversation",
        "401/403 for a non-owner",
        r.status_code in (401, 403),
        "HTTP %d (no ownership check; header ignored)" % r.status_code,
    )


def test_c01_07_employee_cannot_edit_incident():
    reset(rows={IncidentReport: [incident(1)]})
    r = CLIENT.patch(
        "/incidents/1",
        json={"status": "resolved", "severity": "low"},
        headers={"X-Demo-User-Id": "8", "X-Demo-Role": "Employee"},
    )
    changed = r.status_code == 200 and r.json().get("status") == "resolved"
    check(
        "C01-07", "C-01",
        "Employee cannot change incident status/severity",
        "401/403 for the Employee role",
        r.status_code in (401, 403),
        "HTTP %d%s" % (r.status_code, "; incident modified by Employee" if changed else ""),
    )


def test_c01_08_employee_cannot_create_policy():
    session = reset(rows={PolicyVersion: []})
    r = CLIENT.post(
        "/policies",
        json={
            "title": "Unauthorized policy created by Employee",
            "status": "approved",
            "version": {"version_no": "9.9", "body": "Synthetic body."},
        },
        headers={"X-Demo-User-Id": "8", "X-Demo-Role": "Employee"},
    )
    wrote = bool(session.added)
    check(
        "C01-08", "C-01",
        "Employee cannot create or approve a policy",
        "401/403 before any write",
        r.status_code in (401, 403) and not wrote,
        "HTTP %d; in-memory fake recorded %d insert(s), %d commit(s)"
        % (r.status_code, len(session.added), session.committed),
    )


def test_c01_09_employee_cannot_add_policy_version():
    reset(rows={Policy: [policy(1)], PolicyVersion: [version(1)]})
    r = CLIENT.post(
        "/policies/1/versions",
        json={"version_no": "2.0", "body": "Unauthorized revision."},
        headers={"X-Demo-User-Id": "8", "X-Demo-Role": "Employee"},
    )
    check(
        "C01-09", "C-01",
        "Employee cannot publish a new policy version",
        "401/403 for the Employee role",
        r.status_code in (401, 403),
        "HTTP %d" % r.status_code,
    )


def test_c01_10_anonymous_can_resolve_thread():
    session = reset(rows={ClarificationRequest: [clarification(1)]})
    r = CLIENT.post("/clarifications/1/resolve")
    check(
        "C01-10", "C-01",
        "Anonymous caller cannot resolve a clarification thread",
        "401/403 for a non-participant",
        r.status_code in (401, 403),
        "HTTP %d; in-memory thread status now %r"
        % (r.status_code, session.rows[ClarificationRequest][0].status),
    )


def test_c01_11_identity_spoofing_on_reply():
    session = reset(rows={
        ClarificationRequest: [clarification(1, requester=8, assignee=9)],
        User: [user(8), user(9), user(10)],
    })
    r = CLIENT.post(
        "/clarifications/1/replies",
        json={"sender_id": 10, "body": "Posted by someone outside the thread."},
        headers={"X-Demo-User-Id": "10"},
    )
    check(
        "C01-11", "C-01",
        "A non-participant cannot post into a clarification thread",
        "401/403 for sender outside {requester, assignee}",
        r.status_code in (401, 403),
        "HTTP %d; in-memory reply recorded=%s"
        % (r.status_code, any(isinstance(a, ClarificationReply) for a in session.added)),
    )


def test_c01_12_anonymous_dashboard():
    reset()
    r = CLIENT.get("/dashboard/policy-health")
    check(
        "C01-12", "C-01",
        "Anonymous GET /dashboard/policy-health is denied",
        "401/403 for a compliance/admin view",
        r.status_code in (401, 403),
        "HTTP %d" % r.status_code,
    )


def test_c01_13_identity_is_client_supplied():
    """No endpoint may accept a caller-supplied actor id as proof of identity."""
    rows = {User: [user(8), user(9)]}
    session = reset(rows=rows)
    r = CLIENT.post(
        "/clarifications",
        json={"user_id": 9, "reason": "Filed as another employee"},
        headers={"X-Demo-User-Id": "8"},
    )
    check(
        "C01-13", "C-01",
        "Actor identity comes from a verified credential, not the request body",
        "401/403 when body identity conflicts with the caller",
        r.status_code in (401, 403),
        "HTTP %d; %d in-memory insert(s) attributed to user_id=9"
        % (r.status_code, len(session.added)),
    )


def test_c01_14_roles_are_cosmetic():
    """Roles exist in the data model but never gate a request."""
    reset(rows={
        User: [user(8, 1), user(9, 2), user(4, 3)],
        Role: [role(1, "Employee"), role(2, "Policy Owner"), role(3, "System Administrator")],
    })
    employee = CLIENT.get("/users", headers={"X-Demo-Role": "Employee"})
    admin = CLIENT.get("/users", headers={"X-Demo-Role": "System Administrator"})
    check(
        "C01-14", "C-01",
        "Employee and System Administrator receive different authority",
        "Employee denied where admin is allowed (403 vs 200)",
        employee.status_code != admin.status_code,
        "Employee HTTP %d, System Administrator HTTP %d (identical responses)"
        % (employee.status_code, admin.status_code),
    )


def test_c01_15_no_security_scheme_declared():
    """The API contract itself should advertise an authentication scheme."""
    r = CLIENT.get("/openapi.json")
    schemes = ((r.json().get("components") or {}).get("securitySchemes") or {})
    APPENDIX["openapi_security_schemes"] = sorted(schemes)
    check(
        "C01-15", "C-01",
        "OpenAPI contract declares an authentication scheme",
        "at least one security scheme (e.g. bearerAuth)",
        bool(schemes),
        "declared schemes: %s" % (sorted(schemes) or "none"),
    )


# ===========================================================================
# C-02 — Input validation and safe error handling
# ===========================================================================
LEAK_PATTERNS = [
    "Traceback", "psycopg", "postgresql://", "postgres://", "DATABASE_URL",
    "SELECT ", "INSERT INTO", "sqlalchemy", "File \"", "password",
]


def _leaks(text):
    return [p for p in LEAK_PATTERNS if p.lower() in (text or "").lower()]


def post(path, payload, headers=None):
    return CLIENT.post(path, json=payload, headers=headers or {})


def test_c02_01_question_validation():
    session = reset(rows={User: [user(8)]})
    cases = [
        ("blank question", {"user_id": 8, "question": ""}),
        ("whitespace-only question", {"user_id": 8, "question": "     "}),
        ("one-character question", {"user_id": 8, "question": "a"}),
        ("1001-character question", {"user_id": 8, "question": "x" * 1001}),
        ("missing user_id", {"question": "What is the PTO policy?"}),
        ("wrong type user_id", {"user_id": "eight", "question": "What is the PTO policy?"}),
        ("missing question", {"user_id": 8}),
        ("null question", {"user_id": 8, "question": None}),
    ]
    bad = []
    for label, payload in cases:
        r = post("/ask", payload)
        if r.status_code != 422:
            bad.append("%s -> %d" % (label, r.status_code))
    check(
        "C02-01", "C-02",
        "Malformed /ask payloads are rejected with 422",
        "all 8 malformed payloads return 422",
        not bad,
        "unexpected: " + ", ".join(bad) if bad else "all rejected",
    )
    check(
        "C02-02", "C-02",
        "Rejected /ask payloads create no records",
        "0 in-memory inserts",
        len(session.added) == 0 and session.committed == 0,
        "%d insert(s), %d commit(s)" % (len(session.added), session.committed),
    )


def test_c02_03_ask_extra_field_ignored():
    """Unknown fields must not become authority or persisted data."""
    session = reset(rows={User: [user(8)]}, search_rows=[])
    r = post("/ask", {
        "user_id": 8,
        "question": "What is the phishing reporting procedure?",
        "is_admin": True,
        "role": "System Administrator",
    })
    body = r.json() if r.status_code < 500 else {}
    check(
        "C02-03", "C-02",
        "Unknown /ask fields are ignored, not applied",
        "request accepted without granting admin fields",
        "is_admin" not in body and "role" not in body,
        "HTTP %d; response keys=%s" % (r.status_code, sorted(body)[:8]),
    )
    session.committed = 0


def test_c02_04_ask_unknown_user_is_generic():
    session = reset(rows={User: []})
    r = post("/ask", {"user_id": 99999, "question": "What is the PTO policy?"})
    detail = r.json().get("detail") if r.headers.get("content-type", "").startswith("application/json") else ""
    check(
        "C02-04", "C-02",
        "Unknown user is rejected without creating a conversation",
        "404/401 with no records",
        r.status_code in (401, 404) and not session.added,
        "HTTP %d, detail=%r, inserts=%d" % (r.status_code, detail, len(session.added)),
    )


def test_c02_05_feedback_validation():
    base = reset(rows={Message: [], User: [user(8)]})
    cases = [
        ("missing message_id", {"user_id": 8, "rating": True}),
        ("missing rating", {"message_id": 1, "user_id": 8}),
        ("wrong rating type", {"message_id": 1, "user_id": 8, "rating": "maybe"}),
        ("wrong message type", {"message_id": "one", "user_id": 8, "rating": True}),
        ("missing user_id", {"message_id": 1, "rating": True}),
    ]
    bad = []
    for label, payload in cases:
        r = post("/feedback", payload)
        if r.status_code != 422:
            bad.append("%s -> %d" % (label, r.status_code))
    check(
        "C02-05", "C-02",
        "Malformed /feedback payloads are rejected with 422",
        "all 5 malformed payloads return 422",
        not bad,
        "unexpected: " + ", ".join(bad) if bad else "all rejected",
    )
    check(
        "C02-06", "C-02",
        "Rejected /feedback payloads create no records",
        "0 in-memory inserts",
        not base.added,
        "%d insert(s)" % len(base.added),
    )

    r = post("/feedback", {"message_id": 12345, "user_id": 8, "rating": True})
    check(
        "C02-07", "C-02",
        "Feedback for a missing message is refused",
        "404 and no record",
        r.status_code == 404 and not base.added,
        "HTTP %d, inserts=%d" % (r.status_code, len(base.added)),
    )


def test_c02_08_feedback_comment_unbounded():
    session = reset(rows={Message: [object()], User: [user(8)]})
    # Give the fake message an id so the handler accepts it.
    session.rows[Message] = [Message(id=1, conversation_id=1, sender="derexi", body="x")]
    r = post("/feedback", {"message_id": 1, "user_id": 8, "rating": True,
                           "comment": "y" * 50000})
    check(
        "C02-08", "C-02",
        "Overlong feedback comment is rejected",
        "422 for a 50,000-character comment",
        r.status_code == 422,
        "HTTP %d%s" % (r.status_code,
                       "; 50,000 characters accepted and stored in the fake session"
                       if r.status_code == 201 else ""),
    )
    session.committed = 0


def test_c02_09_incident_validation():
    states = reset(rows={User: [user(8)]})
    cases = [
        ("missing reporter", {"description": "Lost laptop"}),
        ("blank description", {"reporter_id": 8, "description": ""}),
        ("one-character description", {"reporter_id": 8, "description": "a"}),
        ("invalid severity", {"reporter_id": 8, "description": "Lost laptop", "severity": "urgent"}),
        ("wrong escalation type", {"reporter_id": 8, "description": "Lost laptop", "escalation_level": "high"}),
        ("missing description", {"reporter_id": 8}),
    ]
    bad = []
    for label, payload in cases:
        r = post("/incidents", payload)
        if r.status_code != 422:
            bad.append("%s -> %d" % (label, r.status_code))
    check(
        "C02-09", "C-02",
        "Malformed /incidents payloads are rejected with 422",
        "all 6 malformed payloads return 422",
        not bad,
        "unexpected: " + ", ".join(bad) if bad else "all rejected",
    )
    check(
        "C02-10", "C-02",
        "Rejected /incidents payloads create no records",
        "0 in-memory inserts",
        not states.added,
        "%d insert(s)" % len(states.added),
    )


def test_c02_12_incident_description_unbounded():
    session = reset(rows={User: [user(8)], IncidentCategory: []})
    r = post("/incidents", {"reporter_id": 8, "description": "z" * 50000})
    check(
        "C02-11", "C-02",
        "Overlong incident description is rejected",
        "422 for a 50,000-character description",
        r.status_code == 422,
        "HTTP %d%s" % (r.status_code,
                       "; 50,000 characters accepted and stored in the fake session"
                       if r.status_code == 201 else ""),
    )
    session.committed = 0


def test_c02_13_reply_validation():
    session = reset(rows={ClarificationRequest: [clarification(1)], User: [user(8)]})
    cases = [
        ("blank body", {"sender_id": 8, "body": ""}),
        ("whitespace body", {"sender_id": 8, "body": "   "}),
        ("2001-character body", {"sender_id": 8, "body": "x" * 2001}),
        ("missing sender", {"body": "hello"}),
        ("wrong sender type", {"sender_id": "eight", "body": "hello"}),
    ]
    bad = []
    for label, payload in cases:
        r = post("/clarifications/1/replies", payload)
        if r.status_code != 422:
            bad.append("%s -> %d" % (label, r.status_code))
    check(
        "C02-12", "C-02",
        "Malformed replies are rejected with 422",
        "all 5 malformed payloads return 422",
        not bad,
        "unexpected: " + ", ".join(bad) if bad else "all rejected",
    )
    check(
        "C02-13", "C-02",
        "Rejected replies create no records",
        "0 in-memory inserts",
        not session.added,
        "%d insert(s)" % len(session.added),
    )


def test_c02_16_policy_payload_validation():
    states = reset(rows={PolicyVersion: []})
    cases = [
        ("wrong version type", {"title": "T", "version": "1.0"}),
        ("missing version", {"title": "T"}),
        ("missing body", {"title": "T", "version": {"version_no": "1.0"}}),
        ("invalid status", {"title": "T", "status": "published",
                            "version": {"version_no": "1.0", "body": "b"}}),
    ]
    bad = []
    for label, payload in cases:
        r = post("/policies", payload)
        if r.status_code != 422:
            bad.append("%s -> %d" % (label, r.status_code))
    check(
        "C02-14", "C-02",
        "Malformed /policies payloads are rejected with 422",
        "all 4 malformed payloads return 422",
        not bad,
        "unexpected: " + ", ".join(bad) if bad else "all rejected",
    )
    check(
        "C02-15", "C-02",
        "Rejected policy payloads create no records",
        "0 in-memory inserts",
        not states.added,
        "%d insert(s)" % len(states.added),
    )


def test_c02_19_policy_title_unbounded():
    session = reset(rows={PolicyVersion: []})
    r = post("/policies", {
        "title": "t" * 100000,
        "version": {"version_no": "1.0", "body": "b"},
    })
    check(
        "C02-16", "C-02",
        "Overlong policy title is rejected",
        "422 for a 100,000-character title",
        r.status_code == 422,
        "HTTP %d%s" % (r.status_code,
                       "; 100,000 characters accepted and stored in the fake session"
                       if r.status_code == 201 else ""),
    )
    session.committed = 0


def test_c02_20_incident_assignment_unchecked():
    """An assignee id must reference a real user before an update is stored."""
    session = reset(rows={IncidentReport: [incident(1)], User: [user(8)]})
    r = CLIENT.patch("/incidents/1", json={"assigned_to": 987654})
    stored = session.rows[IncidentReport][0].assigned_to
    check(
        "C02-17", "C-02",
        "Incident assignment to a nonexistent user is rejected",
        "400/404/422 and no change",
        r.status_code in (400, 404, 422),
        "HTTP %d; in-memory assigned_to=%r" % (r.status_code, stored),
    )


def test_c02_21_error_bodies_are_safe():
    """404/409/422 responses must not expose internals or secrets."""
    reset(rows={Policy: [], Message: [], User: [user(8)]})
    responses = [
        post("/ask", {"user_id": 999, "question": "Question text"}),
        post("/feedback", {"message_id": 999, "user_id": 8, "rating": True}),
        post("/clarifications/999/replies", {"sender_id": 8, "body": "hello"}),
        CLIENT.patch("/incidents/999", json={"status": "resolved"}),
        CLIENT.get("/policies/999"),
        post("/policies/999/versions", {"version_no": "9.9", "body": "b"}),
    ]
    leaks = []
    statuses = []
    for r in responses:
        statuses.append(str(r.status_code))
        found = _leaks(r.text)
        if found:
            leaks.append("%d %s" % (r.status_code, found))
    check(
        "C02-18", "C-02",
        "Error responses contain no stack traces, SQL, or credentials",
        "0 internal details in 6 error responses",
        not leaks,
        ("leaks: " + "; ".join(leaks)) if leaks
        else "statuses %s; no internal details" % ",".join(statuses),
    )


def test_c02_22_error_messages_are_human():
    reset(rows={Policy: [], User: [user(8)]})
    r = CLIENT.get("/policies/424242")
    detail = r.json().get("detail", "") if r.headers.get("content-type", "").startswith("application/json") else ""
    readable = (
        isinstance(detail, str)
        and detail == detail.strip()
        and len(detail) <= 120
        and not re.search(r"[{}\[\]]|Traceback|sqlalchemy", detail)
    )
    check(
        "C02-19", "C-02",
        "Not-found errors use short, employee-readable text",
        "a plain-language detail string",
        r.status_code == 404 and readable,
        "HTTP %d, detail=%r" % (r.status_code, detail),
    )


def test_c02_23_unhandled_database_error_is_safe():
    """A simulated DB outage must yield a generic 500, not an internal trace."""

    class ExplodingSession(FakeSession):
        def query(self, model):
            raise RuntimeError("simulated database outage: postgresql://user:secret@host/db")

    session = ExplodingSession()
    APP.dependency_overrides[main.get_db] = lambda: session
    r = CLIENT.get("/policies")
    leaked = _leaks(r.text)
    check(
        "C02-20", "C-02",
        "Unhandled database failure does not leak internals",
        "HTTP 500 with no traceback, SQL, or connection string",
        r.status_code == 500 and not leaked,
        "HTTP %d, leak markers=%s, body=%r"
        % (r.status_code, leaked or "none", r.text[:80]),
    )
    check(
        "C02-21", "C-02",
        "Unhandled failure gives the employee an actionable message",
        "a plain-language apology/retry message",
        r.status_code == 500 and "try again" in r.text.lower(),
        "HTTP %d, body=%r" % (r.status_code, r.text[:80]),
    )


def test_c02_25_feedback_rating_coercion():
    """Loose bool coercion should not turn arbitrary strings into a rating."""
    session = reset(rows={Message: [Message(id=1, conversation_id=1, sender="derexi", body="x")]})
    r = post("/feedback", {"message_id": 1, "user_id": 8, "rating": "yes"})
    check(
        "C02-22", "C-02",
        "Non-boolean rating values are rejected",
        "422 for rating='yes'",
        r.status_code == 422,
        "HTTP %d; rating coerced and stored=%s"
        % (r.status_code, any(isinstance(a, Feedback) for a in session.added)),
    )
    session.committed = 0


def test_c02_26_schema_field_limits():
    """Inspect declared limits so the report can separate tested from declared."""
    def limits_of(info):
        """Pydantic v2 keeps Field(max_length=…) constraints in metadata."""
        found = {"max_length": None, "min_length": None}
        for constraint in getattr(info, "metadata", []) or []:
            for key in ("max_length", "min_length"):
                value = getattr(constraint, key, None)
                if value is not None:
                    found[key] = value
        return found

    limits = {}
    for name, model in (("AskRequest", schemas.AskRequest),
                        ("FeedbackCreate", schemas.FeedbackCreate),
                        ("IncidentCreate", schemas.IncidentCreate),
                        ("IncidentUpdate", schemas.IncidentUpdate),
                        ("ClarificationCreate", schemas.ClarificationCreate),
                        ("ClarificationReplyCreate", schemas.ClarificationReplyCreate),
                        ("PolicyCreate", schemas.PolicyCreate),
                        ("PolicyVersionCreate", schemas.PolicyVersionCreate),
                        ("PolicyVersionAdd", schemas.PolicyVersionAdd)):
        fields = {}
        for field_name, info in model.model_fields.items():
            fields[field_name] = limits_of(info)
        limits[name] = fields

    free_text = (
        "question", "comment", "description", "body", "title", "summary",
        "reason", "resolution_notes", "topic",
    )
    missing = []
    for model_name, fields in limits.items():
        for field_name, found in fields.items():
            if field_name in free_text and found["max_length"] is None:
                missing.append("%s.%s" % (model_name, field_name))
    APPENDIX["schema_limits"] = limits
    check(
        "C02-23", "C-02",
        "Every free-text field declares an upper bound",
        "0 unbounded free-text fields",
        not missing,
        "unbounded: " + ", ".join(missing) if missing else "all bounded",
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def test_c02_24_empty_policy_fields():
    """An empty title/body must not be stored as an approved-looking policy."""
    session = reset(rows={PolicyVersion: []})
    r = post("/policies", {"title": "", "version": {"version_no": "1.0", "body": ""}})
    check(
        "C02-24", "C-02",
        "Empty policy title and body are rejected",
        "422 for empty title and empty version body",
        r.status_code == 422,
        "HTTP %d%s" % (r.status_code,
                       "; empty policy accepted and stored in the fake session"
                       if r.status_code == 201 else ""),
    )
    session.committed = 0


def test_c02_25_orphan_clarification():
    """A clarification must reference records that exist before it is stored."""
    session = reset(rows={User: [user(8)]})
    r = post("/clarifications", {
        "user_id": 8,
        "message_id": 987654,
        "conversation_id": 987654,
        "policy_id": 987654,
        "reason": "References records that do not exist.",
    })
    check(
        "C02-25", "C-02",
        "Clarification for nonexistent message/conversation/policy is rejected",
        "400/404/422 and no record",
        r.status_code in (400, 404, 422),
        "HTTP %d; %d in-memory insert(s) with dangling foreign keys"
        % (r.status_code, len(session.added)),
    )
    session.committed = 0


def test_c02_26_feedback_unknown_user():
    """Feedback must not be stored against a user id that does not exist."""
    session = reset(rows={
        Message: [Message(id=1, conversation_id=1, sender="derexi", body="x")],
        User: [],
    })
    r = post("/feedback", {"message_id": 1, "user_id": 999999, "rating": True})
    check(
        "C02-26", "C-02",
        "Feedback from a nonexistent user is rejected",
        "404 and no record",
        r.status_code == 404,
        "HTTP %d; %d in-memory insert(s) referencing a missing user"
        % (r.status_code, len(session.added)),
    )
    session.committed = 0


if __name__ == "__main__":
    print("DeRexi security controls — C-01 (RBAC) and C-02 (validation/errors)")
    print("Isolated mode: live database connections are blocked by a tripwire.")
    print("=" * 78)

    # Record the CORS configuration as evidence (names only, no credentials).
    for middleware in APP.user_middleware:
        kwargs = getattr(middleware, "kwargs", {}) or {}
        if "allow_origins" in kwargs:
            APPENDIX["cors_allow_origins"] = list(kwargs.get("allow_origins") or [])
            APPENDIX["cors_allow_credentials"] = bool(kwargs.get("allow_credentials"))
            APPENDIX["cors_allow_methods"] = list(kwargs.get("allow_methods") or [])

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    crashed = 0
    for fn in tests:
        try:
            CURRENT_TEST = fn.__name__
            fn()
        except Exception as exc:  # noqa: BLE001
            crashed += 1
            print("  ERROR " + fn.__name__ + ": " + str(exc))
            traceback.print_exc()
        finally:
            teardown()

    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")
    blocked_n = sum(1 for r in RESULTS if r["status"] == "BLOCKED")
    print("=" * 78)
    print("RESULT: %d passed, %d failed, %d blocked, %d runner errors"
          % (passed, failed, blocked_n, crashed))

    out = os.path.join("evidence", "security_controls_results.json")
    if os.environ.get("SECURITY_EVIDENCE"):
        out = os.environ["SECURITY_EVIDENCE"]
    else:
        out = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                           "docs", "compliance", "evidence", "security_controls_results.json")
        out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({
            "control_c01": "role-based access control",
            "control_c02": "input validation and safe error handling",
            "mode": "isolated (no live database; dependency override + engine tripwire)",
            "appendix": APPENDIX,
            "results": RESULTS,
            "summary": {"passed": passed, "failed": failed,
                        "blocked": blocked_n, "errors": crashed},
        }, fh, indent=2)
    print("Evidence JSON: " + out)
    sys.exit(1 if (failed or crashed) else 0)
