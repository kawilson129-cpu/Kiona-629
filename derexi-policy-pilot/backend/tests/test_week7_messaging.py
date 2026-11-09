"""Week 7 messaging workflow and authorization tests.

Run from backend/:

    ../.venv/bin/python tests/test_week7_messaging.py

Uses isolated in-memory rows and a PostgreSQL connection tripwire. PostgreSQL
syntax is adapted by messaging_fixture; no live database is contacted.
"""

from __future__ import annotations

import os
import sys
import traceback

from messaging_fixture import isolated_database  # locks isolation before main

os.environ["DEREXI_ENV"] = "test"
os.environ["DEREXI_DEV_AUTH"] = "1"
os.environ.setdefault("DEREXI_DEV_USER_IDS", "")

from fastapi.testclient import TestClient
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main  # noqa: E402
from database import get_db  # noqa: E402

RESULTS = []


def check(name, condition, detail=""):
    RESULTS.append((name, bool(condition), detail))
    print(("PASS  " if condition else "FAIL  ") + name + ((" :: " + str(detail)) if detail and not condition else ""))


def main_test():
    engine, offline_factory = isolated_database()
    connection = engine.connect()
    outer = connection.begin()
    TestSession = offline_factory
    TestSession.configure(bind=connection, join_transaction_mode="create_savepoint")

    def override_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_db
    client = TestClient(main.app)

    tokens = {}

    def auth(user_id):
        if user_id not in tokens:
            response = client.post("/dev-auth/token", json={"user_id": user_id})
            assert response.status_code == 200, response.text
            tokens[user_id] = {"Authorization": "Bearer " + response.json()["access_token"]}
        return tokens[user_id]

    def no_auth_headers():
        return {}

    def make_answer_conversation(user_id, policy_id, question, answer):
        """Create a Policy Assistant-style conversation with a citation."""
        version_id = connection.execute(
            text(
                """
                SELECT id FROM policy_versions
                WHERE policy_id = :pid
                ORDER BY created_at DESC, id DESC LIMIT 1
                """
            ),
            {"pid": policy_id},
        ).scalar()
        conversation_id = connection.execute(
            text(
                "INSERT INTO conversations (user_id, topic, status) "
                "VALUES (:uid, :topic, 'open') RETURNING id"
            ),
            {"uid": user_id, "topic": question[:80]},
        ).scalar()
        question_id = connection.execute(
            text(
                "INSERT INTO messages (conversation_id, sender, body) "
                "VALUES (:cid, 'user', :body) RETURNING id"
            ),
            {"cid": conversation_id, "body": question},
        ).scalar()
        answer_id = connection.execute(
            text(
                "INSERT INTO messages (conversation_id, sender, body) "
                "VALUES (:cid, 'derexi', :body) RETURNING id"
            ),
            {"cid": conversation_id, "body": answer},
        ).scalar()
        connection.execute(
            text(
                "INSERT INTO policy_citations (message_id, policy_version_id, excerpt) "
                "VALUES (:mid, :pvid, :excerpt)"
            ),
            {"mid": answer_id, "pvid": version_id, "excerpt": "Test excerpt."},
        )
        return conversation_id, question_id, answer_id

    try:
        # --- Reference / configuration -------------------------------------
        config = client.get("/auth/config")
        check("auth config exposes development mode only with opt-in", config.status_code == 200 and config.json()["dev_auth"] is True)
        check("dev roster returns seeded users", len(client.get("/dev-auth/identities").json()) >= 10)
        check("anonymous /messages is rejected", client.get("/messages").status_code == 401)
        check("anonymous /ask is rejected", client.post("/ask", json={"question": "paid time off"}).status_code == 401)
        check(
            "body identity cannot impersonate another user",
            client.post(
                "/ask",
                json={"user_id": 9, "question": "paid time off"},
                headers=auth(8),
            ).status_code == 403,
        )
        check("employee cannot open admin triage folder", client.get("/messages?folder=triage", headers=auth(8)).status_code == 403)
        check("employee cannot open all-threads folder", client.get("/messages?folder=all", headers=auth(8)).status_code == 403)

        # --- Create a clarification from an answer -------------------------
        sam = 8
        jordan = 9
        rachel = 12
        lucy = 2
        policy_id = 48  # HR policy owned by Jordan Rivera in the seed
        owner_id = connection.execute(
            text("SELECT owner_id FROM policies WHERE id = :pid"), {"pid": policy_id}
        ).scalar()
        check("fixture policy is owned by Jordan", owner_id == jordan, owner_id)

        conversation_id, question_id, answer_id = make_answer_conversation(
            sam,
            policy_id,
            "How do I request an accommodation?",
            "Here's what you should do: submit the accommodation form.\nReference: Employee Leave (v1.0)",
        )
        created = client.post(
            "/clarifications",
            json={
                "conversation_id": conversation_id,
                "policy_id": policy_id,
                "context": "My manager is remote and cannot sign the form.",
            },
            headers=auth(sam),
        )
        check("employee can request clarification from an answer", created.status_code == 201, created.text[:300])
        thread = created.json()
        thread_id = thread["id"]
        check("request routes to the policy owner", thread["assignee"] and thread["assignee"]["id"] == jordan)
        check("thread exposes the owner contact record", bool(thread["assignee"]["email"]) and thread["assignee"]["role"] == "Policy Owner")
        check("escalation starts as awaiting the owner", thread["escalation_status"] == "awaiting_owner", thread["escalation_status"])
        check("originating question is preserved", thread["question"] == "How do I request an accommodation?")
        check("originating answer is preserved", "submit the accommodation form" in (thread["answer"] or ""))
        check("policy citation is preserved", len(thread["citations"]) == 1 and thread["citations"][0]["policy_id"] == policy_id)
        check("requester copy starts read", thread["unread_count"] == 0)
        check("timestamps are present", bool(thread["created_at"]) and bool(thread["updated_at"]))
        # The whole suite shares one transaction, so every now() is the same
        # instant. Move the requester's watermark back one minute to model the
        # real sequence (read now, owner replies later).
        connection.execute(
            text(
                "UPDATE clarification_reads SET last_read_at = now() - interval '1 minute' "
                "WHERE request_id = :rid AND user_id = :uid"
            ),
            {"rid": thread_id, "uid": sam},
        )

        duplicate = client.post(
            "/clarifications",
            json={"conversation_id": conversation_id, "policy_id": policy_id, "context": "again"},
            headers=auth(sam),
        )
        check("duplicate open request is refused", duplicate.status_code == 409, duplicate.text[:200])

        # --- Owner notification and reply ---------------------------------
        jordan_inbox = client.get("/messages?folder=inbox", headers=auth(jordan)).json()
        check(
            "owner inbox contains the thread",
            any(item["id"] == thread_id for item in jordan_inbox["threads"]),
        )
        owner_thread = next(item for item in jordan_inbox["threads"] if item["id"] == thread_id)
        check("new assignment is unread for the owner", owner_thread["unread_count"] >= 1)
        notifications = client.get("/messages/notifications", headers=auth(jordan)).json()
        check(
            "owner receives an in-app assignment notification",
            any(item["thread_id"] == thread_id and item["kind"] == "assigned" for item in notifications["items"]),
        )

        owner_reply = client.post(
            f"/clarifications/{thread_id}/replies",
            json={"body": "Use the electronic signature workflow instead."},
            headers=auth(jordan),
        )
        check("owner can reply", owner_reply.status_code == 201, owner_reply.text[:300])
        check("reply moves thread to in_progress", owner_reply.json()["status"] == "in_progress")

        sam_view = client.get(f"/clarifications/{thread_id}", headers=auth(sam)).json()
        check("employee sees the owner reply", any("electronic signature" in r["body"] for r in sam_view["replies"]))
        check("escalation moves to awaiting the employee", sam_view["escalation_status"] == "awaiting_employee", sam_view["escalation_status"])
        check("employee thread is unread after the reply", sam_view["unread_count"] >= 1)
        sam_notifications = client.get("/messages/notifications", headers=auth(sam)).json()
        check(
            "employee receives a reply notification",
            any(item["thread_id"] == thread_id and item["kind"] == "reply" for item in sam_notifications["items"]),
        )

        mark_read = client.post(f"/clarifications/{thread_id}/read", headers=auth(sam))
        check("employee can mark the thread read", mark_read.status_code == 200 and mark_read.json()["unread_count"] == 0)
        check(
            "unread clears after marking read",
            client.get(f"/clarifications/{thread_id}", headers=auth(sam)).json()["unread_count"] == 0,
        )

        sam_reply = client.post(
            f"/clarifications/{thread_id}/replies",
            json={"body": "Thanks, that works for me."},
            headers=auth(sam),
        )
        check("employee can reply", sam_reply.status_code == 201, sam_reply.text[:300])
        check(
            "owner is notified of the employee reply",
            client.get("/messages/notifications", headers=auth(jordan)).json()["unread_total"] >= 1,
        )
        after_employee = client.get(f"/clarifications/{thread_id}", headers=auth(jordan)).json()
        check("employee reply hands the thread back to the owner", after_employee["escalation_status"] == "awaiting_owner", after_employee["escalation_status"])

        resolved = client.post(f"/clarifications/{thread_id}/resolve", headers=auth(jordan))
        check("owner can resolve", resolved.status_code == 200 and resolved.json()["status"] == "resolved")
        check(
            "resolved thread reports the resolved escalation state",
            client.get(f"/clarifications/{thread_id}", headers=auth(jordan)).json()["escalation_status"] == "resolved",
        )
        closed = client.post(f"/clarifications/{thread_id}/close", headers=auth(jordan))
        check("owner can close a resolved thread", closed.status_code == 200 and closed.json()["status"] == "closed", closed.text[:200])
        check(
            "closed thread reports the closed escalation state",
            client.get(f"/clarifications/{thread_id}", headers=auth(sam)).json()["escalation_status"] == "closed",
        )
        closed_reply = client.post(
            f"/clarifications/{thread_id}/replies",
            json={"body": "one more thing"},
            headers=auth(sam),
        )
        check("reply to a resolved thread is refused", closed_reply.status_code == 409)

        reopened = client.post(
            f"/clarifications/{thread_id}/reopen",
            json={"reason": "The form link expired."},
            headers=auth(sam),
        )
        check("requester can reopen", reopened.status_code == 200 and reopened.json()["status"] == "open")
        reopened_view = client.get(f"/clarifications/{thread_id}", headers=auth(sam)).json()
        check("reopen is recorded in history", any("reopened" in r["body"].lower() or "expired" in r["body"].lower() for r in reopened_view["replies"]))
        check("reopened thread awaits the owner again", reopened_view["escalation_status"] == "awaiting_owner", reopened_view["escalation_status"])

        # --- Escalation filters --------------------------------------------
        awaiting_owner_filter = client.get(
            "/messages?folder=requests&status=awaiting_owner", headers=auth(sam)
        ).json()
        check(
            "status filter selects threads awaiting the owner",
            any(item["id"] == thread_id for item in awaiting_owner_filter["threads"]),
        )
        resolved_filter = client.get(
            "/messages?folder=requests&status=resolved", headers=auth(sam)
        ).json()
        check(
            "status filter excludes threads that are no longer resolved",
            not any(item["id"] == thread_id for item in resolved_filter["threads"]),
        )
        check(
            "unknown escalation status is rejected",
            client.get("/messages?status=bogus", headers=auth(sam)).status_code == 422,
        )
        check(
            "search matches the thread question",
            any(
                item["id"] == thread_id
                for item in client.get("/messages?folder=requests&q=accommodation", headers=auth(sam)).json()["threads"]
            ),
        )

        # --- Isolation -----------------------------------------------------
        check("unrelated owner cannot read the thread", client.get(f"/clarifications/{thread_id}", headers=auth(rachel)).status_code == 404)
        check(
            "unrelated owner cannot reply",
            client.post(
                f"/clarifications/{thread_id}/replies",
                json={"body": "intrusion"},
                headers=auth(rachel),
            ).status_code == 404,
        )
        check("unrelated owner cannot resolve", client.post(f"/clarifications/{thread_id}/resolve", headers=auth(rachel)).status_code == 404)
        check(
            "policy owner cannot use admin assign",
            client.post(
                f"/clarifications/{thread_id}/assign",
                json={"assignee_id": rachel},
                headers=auth(jordan),
            ).status_code == 403,
        )
        check(
            "spoofed sender_id is rejected",
            client.post(
                f"/clarifications/{thread_id}/replies",
                json={"body": "spoof", "sender_id": jordan},
                headers=auth(sam),
            ).status_code == 403,
        )

        # --- Admin oversight and triage -----------------------------------
        admin_view = client.get(f"/clarifications/{thread_id}", headers=auth(lucy))
        check("administrator can read any thread", admin_view.status_code == 200)
        admin_all = client.get("/messages?folder=all", headers=auth(lucy)).json()
        check("administrator sees the organisation-wide list", any(item["id"] == thread_id for item in admin_all["threads"]))
        check("administrator can list the governance queue", client.get("/clarifications", headers=auth(lucy)).status_code == 200)
        check("employee cannot list the governance queue", client.get("/clarifications", headers=auth(sam)).status_code == 403)

        # Missing-owner policy -> triage, then admin assigns it.
        policy_no_owner = connection.execute(
            text(
                "INSERT INTO policies (title, summary, status) "
                "VALUES (:title, 'Week 7 test policy', 'approved') RETURNING id"
            ),
            {"title": "Week 7 Test Policy " + os.urandom(3).hex()},
        ).scalar()
        connection.execute(
            text(
                "INSERT INTO policy_versions (policy_id, version_no, title, body) "
                "VALUES (:pid, '1.0', :title, 'Test body.')"
            ),
            {"pid": policy_no_owner, "title": "Week 7 Test Policy"},
        )
        conv2, _, _ = make_answer_conversation(
            sam, policy_no_owner, "Who owns this policy?", "Reference: Week 7 Test Policy (v1.0)"
        )
        triage_created = client.post(
            "/clarifications",
            json={"conversation_id": conv2, "policy_id": policy_no_owner, "context": "No owner is assigned."},
            headers=auth(sam),
        )
        check("missing owner leaves the thread unassigned", triage_created.status_code == 201 and triage_created.json()["is_triage"] is True, triage_created.text[:300])
        triage_id = triage_created.json()["id"]
        triage = client.get("/messages?folder=triage", headers=auth(lucy)).json()
        check("unassigned thread appears in admin triage", any(item["id"] == triage_id for item in triage["threads"]))
        check(
            "admin can assign a triage thread to a policy owner",
            client.post(
                f"/clarifications/{triage_id}/assign",
                json={"assignee_id": jordan},
                headers=auth(lucy),
            ).status_code == 200,
        )
        check(
            "assigned owner receives the thread",
            any(item["id"] == triage_id for item in client.get("/messages?folder=inbox", headers=auth(jordan)).json()["threads"]),
        )

        # --- Invalid inputs ------------------------------------------------
        check("empty reply is rejected", client.post(f"/clarifications/{thread_id}/replies", json={"body": ""}, headers=auth(sam)).status_code == 422)
        check("unknown folder is rejected", client.get("/messages?folder=bogus", headers=auth(sam)).status_code == 422)
        check(
            "uncited policy is rejected",
            client.post(
                "/clarifications",
                json={"conversation_id": conversation_id, "policy_id": 1, "context": "not cited"},
                headers=auth(sam),
            ).status_code == 422,
        )
        check(
            "short context is rejected",
            client.post(
                "/clarifications",
                json={"conversation_id": conversation_id, "policy_id": policy_id, "context": "x"},
                headers=auth(sam),
            ).status_code == 422,
        )
        check(
            "another user's conversation is not disclosed",
            client.post(
                "/clarifications",
                json={"conversation_id": conversation_id, "context": "steal"},
                headers=auth(rachel),
            ).status_code == 404,
        )

        # --- HTTP method / auth boundaries ---------------------------------
        check("conversation read requires auth", client.get(f"/conversations/{conversation_id}").status_code == 401)
        check("employee can read own conversation", client.get(f"/conversations/{conversation_id}", headers=auth(sam)).status_code == 200)

        # --- Regression: Policy Assistant, Governance, Pulse, Library -----
        ask = client.post(
            "/ask",
            json={"question": "Can I reserve a parking space at headquarters?"},
            headers=auth(sam),
        )
        check("Policy Assistant still answers/routes with auth", ask.status_code == 200 and "needs_clarification" in ask.json(), ask.text[:300])
        check("policy library still lists policies", client.get("/policies", headers=auth(sam)).status_code == 200 and len(client.get("/policies", headers=auth(sam)).json()) > 0)
        check("policy search still works", client.get("/policies/search?q=paid%20time%20off", headers=auth(sam)).status_code == 200)
        check("categories still work", client.get("/categories", headers=auth(sam)).status_code == 200)
        check("governance dashboard is governance-only", client.get("/dashboard/policy-health", headers=auth(sam)).status_code == 403 and client.get("/dashboard/policy-health", headers=auth(lucy)).status_code == 200)
        check("Pulse health endpoint is unaffected", client.get("/api/pulse/health").status_code == 200)
        check("staff directory requires auth", client.get("/users").status_code == 401)
        check("staff emails are admin-only", client.get("/users", headers=auth(sam)).json()[0]["email"] is None)

        # --- Notification body never includes credentials -----------------
        notification_blob = client.get("/messages/notifications", headers=auth(jordan)).text
        check("notification payload has no bearer token", "Bearer " not in notification_blob and "access_token" not in notification_blob)

    finally:
        main.app.dependency_overrides.clear()
        outer.rollback()
        connection.close()

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = len(RESULTS) - passed
    print(f"\n{passed} passed, {failed} failed, {len(RESULTS)} checks")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main_test())
    except Exception:
        traceback.print_exc()
        sys.exit(2)
