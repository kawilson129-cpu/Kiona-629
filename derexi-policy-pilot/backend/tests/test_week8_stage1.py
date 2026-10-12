"""Week 8 Stage 1 — isolated tests for employee incident reporting.

Runs with ZERO writes: no live Supabase is touched. The get_db dependency is
overridden with an in-memory fake session fed by synthetic data, so the real
FastAPI route handlers, request validation, and serialization are exercised
end to end.

Run from backend/:
    python tests/test_week8_stage1.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from fastapi.testclient import TestClient
from models import IncidentCategory, IncidentReport, User
from sqlalchemy.sql import operators

THRESHOLD = main.CONFIDENCE_THRESHOLD


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

    def all(self):
        out = self._rows
        for expr in self._filters:
            col = _col_name(expr)
            val = _col_value(expr)
            if expr.operator is operators.eq and col:
                out = [r for r in out if getattr(r, col) == val]
        return out


class FakeSession:
    def __init__(self, users=(), categories=(), incidents=(), search_rows=()):
        self.users = list(users)
        self.categories = list(categories)
        self.incidents = list(incidents)
        self.search_rows = list(search_rows)
        self.added = []
        self.committed = 0

    def get(self, model, pk):
        if model is User:
            return next((u for u in self.users if getattr(u, "id", None) == pk), None)
        if model is IncidentCategory:
            return next((c for c in self.categories if getattr(c, "id", None) == pk), None)
        return None

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed += 1

    def execute(self, stmt, params=None):
        class _M:
            def __init__(self, rows):
                self._rows = list(rows)

            def mappings(self):
                return self

            def all(self):
                return self._rows

        return _M(self.search_rows)

    def query(self, model):
        return FakeQuery(_ROWS.get(model, []))


def make_user(i, role_id=1):
    u = User()
    u.id = i
    u.first_name = "User"
    u.last_name = str(i)
    u.email = f"u{i}@aurumbank.com"
    u.role_id = role_id
    return u


def make_category(i, name="Phishing or Social Engineering", sev="high"):
    c = IncidentCategory()
    c.id = i
    c.name = name
    c.description = "d"
    c.default_severity = sev
    return c


def search_row(score, pid=17, title="Phishing & Social Engineering Awareness"):
    return {
        "score": score,
        "policy_id": pid,
        "policy_version_id": 99,
        "title": title,
        "version_no": "1.0",
        "body": "The Bank maintains controls to identify and report phishing attempts.",
        "summary": "s",
    }


def reset(users=(), categories=(), incidents=(), search_rows=()):
    app = main.app
    session = FakeSession(users, categories, incidents, search_rows)
    app.dependency_overrides[main.get_db] = lambda: session


# ---------------------------------------------------------------------------
# incident_guidance() — pure logic, no HTTP
# ---------------------------------------------------------------------------
def test_guidance_none_when_no_results():
    reset()
    db = FakeSession(search_rows=[])
    assert main.incident_guidance(db, "clicked a phishing link") is None


def test_guidance_none_below_threshold():
    db = FakeSession(search_rows=[search_row(max(0.0, THRESHOLD - 0.05))])
    assert main.incident_guidance(db, "clicked a phishing link") is None


def test_guidance_returns_best_policy():
    db = FakeSession(search_rows=[search_row(0.55)])
    g = main.incident_guidance(db, "clicked a phishing link")
    assert g is not None
    assert g["policy_id"] == 17
    assert g["title"].startswith("Phishing")
    assert g["score"] == 0.55
    assert isinstance(g["excerpt"], str) and g["excerpt"]


# ---------------------------------------------------------------------------
# POST /incidents — via TestClient + fake session
# ---------------------------------------------------------------------------
def test_post_incident_reporter_missing():
    reset(users=[make_user(8)], categories=[make_category(1)])
    r = TestClient(main.app).post(
        "/incidents", json={"reporter_id": 99, "category_id": 1, "description": "Lost laptop"}
    )
    assert r.status_code == 404


def test_post_incident_category_missing():
    reset(users=[make_user(8)], categories=[])
    r = TestClient(main.app).post(
        "/incidents", json={"reporter_id": 8, "category_id": 5, "description": "Lost laptop"}
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "Incident category not found"


def test_post_incident_ok_default_severity_and_guidance():
    reset(
        users=[make_user(8)],
        categories=[make_category(1, sev="high")],
        search_rows=[search_row(0.5)],
    )
    r = TestClient(main.app).post(
        "/incidents",
        json={
            "reporter_id": 8,
            "category_id": 1,
            "description": "Clicked a phishing link and entered my password",
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "reported"
    assert body["severity"] == "high"
    assert body["guidance"] is not None
    assert body["guidance"]["policy_id"] == 17


def test_post_incident_explicit_severity_wins():
    reset(users=[make_user(8)], categories=[make_category(1, sev="high")])
    r = TestClient(main.app).post(
        "/incidents",
        json={"reporter_id": 8, "category_id": 1, "description": "Lost device", "severity": "low"},
    )
    assert r.status_code == 201
    assert r.json()["severity"] == "low"


# ---------------------------------------------------------------------------
# GET /incidents?reporter_id= — scoping
# ---------------------------------------------------------------------------
def test_get_incidents_reporter_scoped():
    inc = IncidentReport(
        reporter_id=8, category_id=1, description="a", severity="high", status="reported"
    )
    other = IncidentReport(
        reporter_id=9, category_id=2, description="b", severity="medium", status="reported"
    )
    _ROWS.clear()
    _ROWS.update({IncidentReport: [inc, other], IncidentCategory: []})
    reset(users=[make_user(8), make_user(9)], incidents=[inc, other])
    r = TestClient(main.app).get("/incidents?reporter_id=8")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["reporter_id"] == 8
    _ROWS.clear()


def test_get_incident_categories():
    cats = [make_category(1), make_category(2, name="Malware", sev="critical")]
    _ROWS.clear()
    _ROWS.update({IncidentCategory: cats, IncidentReport: []})
    reset(categories=cats)
    r = TestClient(main.app).get("/incident-categories")
    assert r.status_code == 200
    assert [c["name"] for c in r.json()] == ["Phishing or Social Engineering", "Malware"]


_ROWS = {
    IncidentReport: [],
    IncidentCategory: [],
}


if __name__ == "__main__":
    import traceback

    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            main.app.dependency_overrides.clear()
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
            traceback.print_exc()
    total = len(fns)
    print(f"\n{total - failed} passed, {failed} failed")
    sys.exit(1 if failed else 0)