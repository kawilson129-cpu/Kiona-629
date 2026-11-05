"""Assignment 5: real secured handlers, signed synthetic identities, disposable DB.

Run from backend/: ../.venv/bin/python tests/test_assignment5_controls.py
PostgreSQL ranking is substituted with deterministic approved-policy rows;
authorization, transactions, state rules and response serialization are real.
"""
import unittest
from unittest.mock import patch

import test_secure_api as secured
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

main, m = secured.main, secured.m


class Assignment5Tests(unittest.TestCase):
    def setUp(self):
        self.fixture = secured.SecuredTests()
        self.fixture.setUp()
        self.client, self.factory, self.auth = self.fixture.client, self.fixture.factory, self.fixture.auth
        # Only the PostgreSQL search dialect is substituted, never permissions.
        search = text("SELECT p.id AS policy_id, p.title, v.id AS policy_version_id, "
                      "v.version_no, v.body, 0.7 AS score FROM policies p JOIN policy_versions v "
                      "ON v.policy_id=p.id WHERE p.status='approved'")
        self.lookup = patch.object(main, "SEARCH_SQL", search)
        self.lookup.start()
        self.addCleanup(self.lookup.stop)

    def tearDown(self):
        self.fixture.tearDown()

    def snapshot(self):
        with self.factory() as db:
            return [(i.id, i.reporter_id, i.assigned_to, i.status, i.severity,
                     i.escalation_level, i.resolution_notes, i.updated_at)
                    for i in db.scalars(select(m.IncidentReport).order_by(m.IncidentReport.id))]

    def reject(self, changes, code, uid=91003, incident=90001):
        before = self.snapshot()
        response = self.client.patch(f"/incidents/{incident}", json=changes, headers=self.auth(uid))
        self.assertEqual(response.status_code, code, response.text)
        self.assertEqual(self.snapshot(), before, "Rejected action changed incident data")
        return response

    def update(self, changes, uid=91003):
        response = self.client.patch("/incidents/90001", json=changes, headers=self.auth(uid))
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_A501_private_incident_denial(self):
        """Unrelated employee gets 404 without private content or mutations."""
        response = self.reject({"resolution_notes": "Unauthorized note"}, 404, uid=91004)
        self.assertNotIn("Synthetic incident", response.text)
        self.assertEqual(self.client.get("/incidents", headers=self.auth(91004)).json()[0]["id"], 90002)

    def test_A502_creation_validation(self):
        """Invalid actor/category/severity/blank text/high initial level cannot create rows."""
        base = {"reporter_id": 91001, "description": "Report phishing immediately", "category_id": 97001}
        for delta, code in (({"reporter_id": 91004}, 403), ({"category_id": 99999}, 404),
                            ({"severity": "urgent"}, 422), ({"description": " "}, 422),
                            ({"escalation_level": 2}, 403)):
            before = self.snapshot()
            response = self.client.post("/incidents", json={**base, **delta}, headers=self.auth())
            self.assertEqual(response.status_code, code, response.text)
            self.assertEqual(before, self.snapshot())

    def test_A503_guidance_intake_and_no_ai(self):
        """Valid self-report persists level 1/category severity with grounded reference; no AI call."""
        with patch.object(main.ai, "generate_answer") as ai:
            response = self.client.post("/incidents", headers=self.auth(), json={
                "reporter_id": 91001, "category_id": 97001, "description": "Report phishing immediately"})
            ai.assert_not_called()
        self.assertEqual(response.status_code, 201, response.text)
        data = response.json()
        self.assertEqual((data["reporter_id"], data["status"], data["severity"], data["escalation_level"]),
                         (91001, "reported", "high", 1))
        self.assertEqual(data["guidance"]["policy_version_id"], 94001)
        self.assertIn("Suggested policy reference only", data["guidance"]["notice"])
        self.assertNotIn("Private synthetic", response.text)
        with self.factory() as db:
            self.assertEqual(db.get(m.IncidentReport, data["id"]).description, "Report phishing immediately")

    def test_A504_assignment_authorization(self):
        """Assigned handler cannot reassign; admin can; invalid assignee cannot partially mutate."""
        self.reject({"assigned_to": 91003}, 403, uid=91002)
        self.reject({"assigned_to": 99999, "status": "triaged"}, 404)
        self.assertEqual(self.update({"assigned_to": 91003})["assigned_to"], 91003)

    def test_A505_escalation_authorization(self):
        """Handler cannot escalate through status or level; admin can set a coherent pair."""
        for body in ({"status": "escalated", "escalation_level": 2}, {"escalation_level": 2}):
            self.reject(body, 403, uid=91002)
        data = self.update({"status": "escalated", "escalation_level": 2})
        self.assertEqual((data["status"], data["escalation_level"]), ("escalated", 2))

    def test_A506_invalid_state_pairs(self):
        """Escalated/level 1 and reported-or-triaged/level 2 are rejected atomically."""
        for changes in ({"status": "escalated"}, {"status": "triaged", "escalation_level": 2},
                        {"escalation_level": 2}):
            self.reject(changes, 422)

    def test_A507_triage_before_resolution(self):
        """Reported cannot jump directly to resolved; assigned handler may triage then resolve."""
        self.reject({"status": "resolved"}, 409)
        self.update({"status": "triaged"}, uid=91002)
        self.assertEqual(self.update({"status": "resolved", "resolution_notes": "Synthetic review complete"},
                                    uid=91002)["status"], "resolved")

    def test_A508_resolved_is_terminal(self):
        """Resolved cases cannot reopen, but notes and idempotent resolved remain compatible."""
        self.update({"status": "triaged"})
        self.update({"status": "resolved"})
        self.reject({"status": "triaged"}, 409)
        self.update({"status": "resolved", "resolution_notes": "Follow-up note"}, uid=91002)

    def test_A509_escalated_closure_authority(self):
        """Handler can annotate escalated case; only admin can close or change its level."""
        self.update({"status": "escalated", "escalation_level": 2})
        self.update({"resolution_notes": "Evidence reviewed", "severity": "high"}, uid=91002)
        self.reject({"status": "resolved"}, 403, uid=91002)
        self.reject({"escalation_level": 3}, 403, uid=91002)
        self.assertEqual(self.update({"status": "resolved"})["escalation_level"], 2)

    def test_A510_clarification_privacy(self):
        """Nonparticipants including admin cannot read private thread; oversight metadata omits bodies."""
        for uid in (91003, 91004):
            response = self.client.get("/clarifications/94010", headers=self.auth(uid))
            self.assertEqual(response.status_code, 404, response.text)
            self.assertNotIn("Private synthetic thread", response.text)
        response = self.client.get("/admin/clarifications", headers=self.auth(91003))
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn("Private synthetic thread", response.text)

    def test_A511_feedback_ownership(self):
        """Another employee cannot rate a private answer; denied request inserts no feedback."""
        before = self.fixture.fixture.counts()
        response = self.client.post("/feedback", headers=self.auth(91004), json={
            "user_id": 91004, "message_id": 99001, "rating": True})
        self.assertEqual(response.status_code, 404, response.text)
        self.assertEqual(before, self.fixture.fixture.counts())

    def test_A512_safe_database_outage(self):
        """Database error becomes sanitized 503, without private error details."""
        def broken_db():
            raise SQLAlchemyError("Synthetic private DSN and password marker")
            yield
        self.fixture.app.dependency_overrides[main.get_db] = broken_db
        response = self.client.get("/incidents", headers=self.auth())
        self.assertEqual(response.status_code, 503, response.text)
        self.assertNotIn("password", response.text)
        self.assertNotIn("DSN", response.text)

    def test_A513_guidance_gate(self):
        """Empty, weak or unrelated evidence yields no guidance; approved matching reference is returned."""
        from test_week8_stage1 import FakeSession, search_row
        for rows in ([], [search_row(0.1)], [search_row(0.9, title="Unrelated")]):
            query = "gym membership reimbursement" if rows and rows[0]["score"] == 0.9 else "phishing"
            self.assertIsNone(main.incident_guidance(FakeSession(search_rows=rows), query))
        guide = main.incident_guidance(FakeSession(search_rows=[search_row(0.6)]), "phishing")
        self.assertEqual(guide["policy_id"], 17)

    def test_A514_lookup_failure_before_write(self):
        """Reference lookup failure yields safe 503 and no partial incident insert."""
        with patch.object(main, "incident_guidance", side_effect=SQLAlchemyError("private marker")):
            before = self.snapshot()
            response = self.client.post("/incidents", headers=self.auth(), json={
                "reporter_id": 91001, "description": "Report phishing immediately"})
            self.assertEqual(response.status_code, 503, response.text)
            self.assertNotIn("private marker", response.text)
            self.assertEqual(before, self.snapshot())

    def test_A515_legacy_notes_without_rewrite(self):
        """An inconsistent legacy pair permits notes; no status/level repair is silently persisted."""
        with self.factory.begin() as db:
            item = db.get(m.IncidentReport, 90001)
            item.status, item.escalation_level = "escalated", 1
        data = self.update({"resolution_notes": "Historical evidence noted"}, uid=91002)
        self.assertEqual((data["status"], data["escalation_level"]), ("escalated", 1))

    def test_A516_role_and_identity_preservation(self):
        """Employee/owner/admin names and synthetic IDs persist; anonymous and forged roles fail closed."""
        self.assertEqual(self.client.get("/incidents").status_code, 401)
        response = self.client.get("/dashboard/policy-health", headers=self.auth(role="System Administrator"))
        self.assertEqual(response.status_code, 403, response.text)
        with self.factory() as db:
            self.assertEqual(set(db.scalars(select(m.Role.name))), {"Employee", "Policy Owner", "System Administrator"})
            self.assertEqual(set(db.scalars(select(m.User.id))), {91001, 91002, 91003, 91004})


class Assignment5DemoTests(unittest.TestCase):
    def setUp(self):
        self.fixture = secured.DemoTests()
        self.fixture.setUp()

    def tearDown(self):
        self.fixture.tearDown()

    def test_A517_demo_incident_and_persona_switch(self):
        """Local lexical lookup supports incident intake; switch keeps own incident scope and source bytes unchanged."""
        fixture = self.fixture
        session = fixture.login()
        headers = {"Origin": "http://127.0.0.1:8000", "X-CSRF-Token": session["csrf"]}
        response = fixture.local.post("/incidents", headers=headers, json={
            "reporter_id": 91001, "description": "Report phishing messages immediately"})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["guidance"]["policy_version_id"], 94001)
        incident_id = response.json()["id"]
        response = fixture.local.post("/__dev/switch", json={"user_id": 91004}, headers=headers)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(fixture.local.get("/me").json()["user_id"], 91004)
        self.assertNotIn(incident_id, [i["id"] for i in fixture.local.get("/incidents").json()])


if __name__ == "__main__":
    unittest.main(verbosity=2)
