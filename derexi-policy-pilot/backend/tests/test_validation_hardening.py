"""C-02 regressions against the real API and disposable SQLite transactions.

These are new checks, not a replacement claim for the unavailable original 26.
Run from backend/: ../.venv/bin/python tests/test_validation_hardening.py
"""
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "postgresql+psycopg2://offline:offline@127.0.0.1:1/offline"

with patch("dotenv.load_dotenv"):
    import main
    import models as m
    from database import Base

from fastapi.testclient import TestClient
from sqlalchemy import BigInteger, create_engine, event, func, select, text
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError


@compiles(BigInteger, "sqlite")
def local_integer(type_, compiler, **kw):
    # SQLite's autoincrement requires the exact INTEGER spelling; ORM unchanged.
    return "INTEGER"


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        @event.listens_for(self.engine, "connect")
        def foreign_keys(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.factory = sessionmaker(bind=self.engine)
        with self.factory.begin() as db:
            db.add(m.Department(id=93001, name="Synthetic department"))
            db.add(m.Role(id=92001, name="Employee"))
            db.flush()
            db.add_all([m.User(id=i, first_name="Synthetic", last_name=str(i),
                               email=f"{i}@example.invalid", department_id=93001, role_id=92001)
                        for i in (91001, 91002)])
            db.add(m.IncidentCategory(id=97001, name="Synthetic category", default_severity="high"))
            db.add(m.PolicyCategory(id=98001, name="Synthetic category"))
            db.flush()
            db.add(m.Conversation(id=96001, user_id=91001))
            db.add(m.Policy(id=95001, title="Synthetic existing", owner_id=91001, status="draft"))
            db.flush()
            db.add_all([m.Message(id=99001, conversation_id=96001, sender="derexi", body="Synthetic answer"),
                        m.Message(id=99002, conversation_id=96001, sender="user", body="Synthetic question")])
            db.add(m.IncidentReport(id=90001, reporter_id=91001, category_id=97001, description="Synthetic incident"))
        def local_db():
            with self.factory() as db:
                yield db
        main.app.dependency_overrides[main.get_db] = local_db
        self.client = TestClient(main.app, raise_server_exceptions=False)

    def tearDown(self):
        self.client.close()
        main.app.dependency_overrides.clear()
        self.engine.dispose()

    def counts(self):
        with self.factory() as db:
            return tuple(db.scalar(select(func.count()).select_from(model)) for model in
                         (m.Policy, m.PolicyVersion, m.Feedback, m.ClarificationRequest, m.IncidentReport))

    def rejected(self, path, body, expected=422, method="POST"):
        before = self.counts()
        response = self.client.request(method, path, json=body)
        self.assertEqual(response.status_code, expected, response.text)
        self.assertEqual(before, self.counts(), "Rejected request mutated persistent rows")
        return response

    def policy(self, **changes):
        return {"title": "Synthetic new policy", "owner_id": 91001,
                "category_id": 98001, "version": {"body": "Valid synthetic policy body", "created_by": 91001}, **changes}

    def test_valid_policy_and_version_persist(self):
        response = self.client.post("/policies", json=self.policy())
        self.assertEqual(response.status_code, 201, response.text)
        pid = response.json()["id"]
        response = self.client.post(f"/policies/{pid}/versions", json={"version_no": "1.1", "body": "Updated synthetic body", "created_by": 91001})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(self.counts()[:2], (2, 2))

    def test_blank_and_oversize_policy_title(self):
        for title in ("", " \n\t ", "x" * 201):
            self.rejected("/policies", self.policy(title=title))

    def test_blank_and_oversize_policy_body(self):
        for body in ("", " \n\t ", "x" * 100001):
            self.rejected("/policies", self.policy(version={"body": body}))

    def test_summary_and_version_title_limits(self):
        self.rejected("/policies", self.policy(summary="x" * 2001))
        self.rejected("/policies", self.policy(version={"body": "Valid", "title": " "}))
        self.rejected("/policies", self.policy(version={"body": "Valid", "title": "x" * 201}))

    def test_policy_reference_validation(self):
        for payload in (self.policy(owner_id=99999), self.policy(category_id=99999),
                        self.policy(version={"body": "Valid", "created_by": 99999})):
            self.rejected("/policies", payload, 404)

    def test_version_reference_validation(self):
        self.rejected("/policies/95001/versions", {"version_no": "1.1", "body": "Valid", "created_by": 99999}, 404)
        self.rejected("/policies/99999/versions", {"version_no": "1.1", "body": "Valid"}, 404)

    def test_version_lengths_and_blanks(self):
        for version in ("", "  ", "x" * 41):
            self.rejected("/policies/95001/versions", {"version_no": version, "body": "Valid"})
        self.rejected("/policies/95001/versions", {"version_no": "1.1", "body": " "})

    def test_strict_feedback_boolean_and_comment_limit(self):
        base = {"message_id": 99001, "user_id": 91001}
        for rating in ("true", "false", 1, 0, None, [], {}):
            self.rejected("/feedback", {**base, "rating": rating})
        self.rejected("/feedback", {**base, "rating": True, "comment": "x" * 2001})

    def test_legitimate_feedback(self):
        for rating in (True, False):
            response = self.client.post("/feedback", json={"message_id": 99001, "user_id": 91001, "rating": rating})
            self.assertEqual(response.status_code, 201, response.text)

    def test_feedback_references_and_conversation_consistency(self):
        for msg, uid, code in ((99999, 91001, 404), (99001, 99999, 404),
                               (99001, 91002, 422), (99002, 91001, 422)):
            self.rejected("/feedback", {"message_id": msg, "user_id": uid, "rating": True}, code)

    def test_clarification_references(self):
        for field in ("user_id", "assigned_to", "policy_id", "message_id", "conversation_id"):
            self.rejected("/clarifications", {"user_id": 91001, field: 99999}, 404)

    def test_clarification_linked_ownership(self):
        self.rejected("/clarifications", {"user_id": 91002, "conversation_id": 96001}, 422)
        self.rejected("/clarifications", {"user_id": 91001, "conversation_id": 96001, "message_id": 99001}, 422)

    def test_legitimate_clarification_infers_own_conversation(self):
        response = self.client.post("/clarifications", json={"user_id": 91001, "message_id": 99002, "policy_id": 95001, "assigned_to": 91002})
        self.assertEqual(response.status_code, 201, response.text)
        with self.factory() as db:
            request = db.get(m.ClarificationRequest, response.json()["id"])
            self.assertEqual(request.conversation_id, 96001)

    def test_clarification_text_and_reply_validation(self):
        for reason in (" ", "x" * 1001):
            self.rejected("/clarifications", {"user_id": 91001, "reason": reason})
        for body in (" ", "x" * 2001):
            self.rejected("/clarifications/99999/replies", {"sender_id": 91001, "body": body})

    def test_incident_references(self):
        for field in ("reporter_id", "assigned_to", "category_id"):
            self.rejected("/incidents", {"reporter_id": 91001, "description": "Valid synthetic incident", field: 99999}, 404)

    # SQLite lacks pg_trgm; an empty reference lookup isolates intake validation.
    @patch.object(main, "SEARCH_SQL", text("SELECT 1 WHERE 0"))
    def test_legitimate_incident_and_update(self):
        response = self.client.post("/incidents", json={"reporter_id": 91001, "description": "Valid synthetic incident", "category_id": 97001})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["severity"], "high")
        response = self.client.patch("/incidents/90001", json={"assigned_to": 91002, "resolution_notes": "Synthetic note"})
        self.assertEqual(response.status_code, 200, response.text)

    def test_update_invalid_assignment_does_not_partially_mutate(self):
        self.rejected("/incidents/90001", {"assigned_to": 99999, "status": "resolved"}, 404, "PATCH")
        with self.factory() as db:
            self.assertEqual(db.get(m.IncidentReport, 90001).status, "reported")

    def test_incident_text_limits(self):
        for description in (" ", "x" * 10001):
            self.rejected("/incidents", {"reporter_id": 91001, "description": description})
        self.rejected("/incidents/90001", {"resolution_notes": "x" * 10001}, method="PATCH")

    def test_incident_null_empty_and_invalid_enum_updates(self):
        for payload in ({}, {"status": None}, {"severity": None}, {"escalation_level": None},
                        {"status": "invalid"}, {"severity": "invalid"}, {"escalation_level": 11}):
            self.rejected("/incidents/90001", payload, method="PATCH")

    def test_strict_positive_ids(self):
        for uid in (0, -1, True, "91001", 1.5, 2**63):
            self.rejected("/incidents", {"reporter_id": uid, "description": "Valid synthetic"})

    def test_unknown_fields_rejected(self):
        self.rejected("/policies", self.policy(role="System Administrator"))

    def test_questions_and_topic_limits(self):
        for question in (" ", "x" * 1001):
            self.rejected("/ask", {"user_id": 91001, "question": question})
        self.rejected("/ask", {"user_id": 91001, "question": "Valid question?", "topic": "x" * 1001})

    def test_ask_unknown_user_is_rejected_before_write(self):
        self.rejected("/ask", {"user_id": 99999, "question": "Valid question?"}, 404)

    def test_assistant_answer_feedback_and_conversation_workflow(self):
        # PostgreSQL pg_trgm is not available in SQLite. Supply deterministic
        # search rows while exercising the unchanged real /ask transaction.
        with self.factory.begin() as db:
            db.get(m.Policy, 95001).status = "approved"
            db.add(m.PolicyVersion(id=94001, policy_id=95001, version_no="1.0",
                                   title="Synthetic phishing policy",
                                   body="Report phishing messages immediately to the security team."))
        search = text("SELECT p.id AS policy_id, p.title, p.summary, v.id AS policy_version_id, "
                      "v.version_no, v.body, 0.7 AS score FROM policies p JOIN policy_versions v "
                      "ON v.policy_id=p.id WHERE p.status='approved'")
        with patch.object(main, "SEARCH_SQL", search), patch.object(main.ai, "generate_answer", return_value=None):
            response = self.client.post("/ask", json={"user_id": 91001, "question": "How do I report phishing?"})
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertFalse(result["needs_clarification"])
        self.assertEqual(result["citations"][0]["policy_id"], 95001)
        conversation = self.client.get(f'/conversations/{result["conversation_id"]}')
        self.assertEqual(conversation.status_code, 200)
        self.assertEqual(len(conversation.json()["messages"]), 2)
        response = self.client.post("/feedback", json={"user_id": 91001,
                                    "message_id": result["derexi_message_id"], "rating": True})
        self.assertEqual(response.status_code, 201, response.text)

    def test_assistant_fallback_clarification_reply_and_resolution_workflow(self):
        empty_search = text("SELECT 1 WHERE 0")
        with patch.object(main, "SEARCH_SQL", empty_search):
            response = self.client.post("/ask", json={"user_id": 91001, "question": "An unknown synthetic policy question?"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["needs_clarification"])
        tid = response.json()["clarification_request_id"]
        response = self.client.post(f"/clarifications/{tid}/replies", json={"sender_id": 91001, "body": "A legitimate synthetic reply"})
        self.assertEqual(response.status_code, 201, response.text)
        response = self.client.post(f"/clarifications/{tid}/resolve")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "resolved")

    def test_pulse_api_runs_integrity_pipeline_and_static_ui_is_preserved(self):
        from pulse import service
        url = "https://www.fdic.gov/news/example"
        import xml.etree.ElementTree as ET
        fixture = ET.fromstring(f"<rss><channel><item><title>FDIC news</title><link>{url}</link></item></channel></rss>")
        previous = service._cache
        service._cache = {}
        try:
            with patch.object(service, "SOURCES", {"FDIC": service.SOURCES["FDIC"]}), \
                 patch.object(service, "fetch_source", return_value=fixture), \
                 patch("pulse.integrity.article_destination", return_value=url):
                response = self.client.get("/api/pulse")
                self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(response.json()["articles"][0]["source"], "FDIC")
                self.assertEqual(response.json()["articles"][0]["url"], url)
        finally:
            service._cache = previous
        self.assertEqual(self.client.get("/ui/").status_code, 200)
        script = self.client.get("/ui/app.js").text
        self.assertIn("function choosePersona", script)

    def test_safe_validation_errors_do_not_echo_input(self):
        marker = "synthetic-sensitive-input-" * 200
        response = self.rejected("/policies", self.policy(title=marker))
        self.assertNotIn(marker, response.text)
        self.assertNotIn('"input"', response.text)

    def test_safe_database_errors(self):
        def broken_db():
            raise SQLAlchemyError("synthetic confidential connection details")
            yield
        main.app.dependency_overrides[main.get_db] = broken_db
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("confidential", response.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
