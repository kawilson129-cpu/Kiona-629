"""Real secured API and local-session regressions over disposable synthetic data."""
import dataclasses
import os
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
import main
import models as m
from auth import AuthSettings, SupabaseJWTVerifier
from secure_api import create_app
from dev_demo import build_demo, COOKIE
import test_validation_hardening as fixtures


class SecuredTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ValidationTests()
        self.fixture.setUp()
        self.factory = self.fixture.factory
        with self.factory.begin() as db:
            db.add_all([m.Role(id=92002, name="Policy Owner"), m.Role(id=92003, name="System Administrator")])
            db.flush()
            db.get(m.User, 91002).role_id = 92002
            db.add_all([m.User(id=uid, first_name="Synthetic", last_name=str(uid), email=f"{uid}@example.invalid",
                               role_id=rid, department_id=93001) for uid, rid in ((91003,92003),(91004,92001))])
            db.get(m.Policy, 95001).owner_id = 91002
            db.add(m.Policy(id=95002, title="Synthetic approved phishing", owner_id=91002, status="approved"))
            db.add(m.Policy(id=95003, title="Synthetic unrelated draft", owner_id=91003, status="draft"))
            db.add(m.Conversation(id=96002, user_id=91004))
            db.flush()
            db.add(m.PolicyVersion(id=94001, policy_id=95002, version_no="1.0", title="Synthetic approved phishing",
                                   body="Report phishing messages immediately to the security team."))
            db.add(m.Message(id=99003, conversation_id=96002, sender="user", body="Private synthetic question"))
            db.add(m.ClarificationRequest(id=94010,user_id=91001,assigned_to=91002,reason="Private synthetic thread",conversation_id=96001,message_id=99002))
            db.add(m.ClarificationRequest(id=94011,user_id=91004,assigned_to=91003,reason="Unrelated private thread"))
            db.get(m.IncidentReport, 90001).assigned_to = 91002
            db.add(m.IncidentReport(id=90002,reporter_id=91004,description="Unrelated private incident"))
        self.key = ec.generate_private_key(ec.SECP256R1())
        keys = Mock()
        keys.get_signing_key_from_jwt.return_value = Mock(key=self.key.public_key())
        self.settings = AuthSettings("https://synthetic.invalid", "https://synthetic.invalid/jwks", "https://synthetic.invalid/auth/v1")
        self.mapping = {f"synthetic-{uid}":uid for uid in (91001,91002,91003,91004)}
        self.app = create_app(SupabaseJWTVerifier(self.settings,jwk_client=keys), self.mapping)
        self.app.dependency_overrides[main.get_db] = self.local_db
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def local_db(self):
        with self.factory() as db:
            yield db

    def tearDown(self):
        self.client.close()
        self.fixture.tearDown()

    def auth(self, uid=91001, **claims):
        payload={"sub":f"synthetic-{uid}","iat":int(time.time()),"exp":int(time.time())+3600,
                 "iss":self.settings.issuer,"aud":self.settings.audience,**claims}
        return {"Authorization":"Bearer "+jwt.encode(payload,self.key,algorithm="ES256",headers={"kid":"synthetic"})}

    def test_missing_credentials_all_protected_routes(self):
        for method,path in [("GET","/users"),("GET","/policies"),("POST","/policies"),
                            ("POST","/ask"),("GET","/incidents"),("POST","/incidents"),
                            ("GET","/clarifications"),("GET","/conversations/96001"),
                            ("GET","/api/pulse"),("GET","/health"),("GET","/me")]:
            self.assertEqual(self.client.request(method,path).status_code,401,path)

    def test_invalid_expired_wrong_issuer_and_audience(self):
        for override in ({"exp":int(time.time())-60},{"iss":"urn:local-demo"},{"aud":"other"}):
            self.assertEqual(self.client.get("/users",headers=self.auth(**override)).status_code,401)
        self.assertEqual(self.client.get("/users",headers={"Authorization":"Bearer unsigned"}).status_code,401)

    def test_no_unsigned_demo_header_or_cookie_identity(self):
        self.assertEqual(self.client.get("/users",headers={"X-Demo-User-Id":"91003","X-Demo-Role":"System Administrator"}).status_code,401)
        self.client.cookies.set(COOKIE,"not-a-production-credential")
        self.assertEqual(self.client.get("/users").status_code,401)
        self.assertEqual(self.client.get("/__dev/session").status_code,404)

    def test_verified_principal_and_minimal_directory(self):
        response=self.client.get("/me",headers=self.auth())
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["role"],"Employee")
        response=self.client.get("/users",headers=self.auth())
        self.assertNotIn("email",response.text)
        self.assertEqual(len(response.json()),4)

    def test_claimed_role_is_ignored_and_unknown_mapping_denied(self):
        self.assertEqual(self.client.get("/dashboard/policy-health",headers=self.auth(role="System Administrator")).status_code,403)
        self.assertEqual(self.client.get("/users",headers=self.auth(sub="unlinked")).status_code,403)

    def test_unknown_server_role_fails_closed(self):
        with self.factory.begin() as db:
            db.get(m.Role,92001).name="Developer"
        self.assertEqual(self.client.get("/me",headers=self.auth()).status_code,403)

    def test_policy_visibility_list_details_and_categories(self):
        self.assertEqual([p["id"] for p in self.client.get("/policies",headers=self.auth()).json()],[95002])
        self.assertEqual(self.client.get("/policies/95001",headers=self.auth()).status_code,404)
        self.assertEqual(self.client.get("/policies/95001",headers=self.auth(91002)).status_code,200)
        self.assertEqual(self.client.get("/policies/95003",headers=self.auth(91002)).status_code,404)
        self.assertEqual(len(self.client.get("/policies",headers=self.auth(91003)).json()),3)
        self.assertEqual(self.client.get("/categories",headers=self.auth()).status_code,200)

    def test_employee_policy_write_and_impersonation_denied_before_write(self):
        before=self.fixture.counts()
        body=self.fixture.policy()
        self.assertEqual(self.client.post("/policies",json=body,headers=self.auth()).status_code,403)
        self.assertEqual(self.client.post("/ask",json={"user_id":91002,"question":"A policy question?"},headers=self.auth()).status_code,403)
        self.assertEqual(before,self.fixture.counts())

    def test_owner_draft_creation_stores_verified_author_and_owner(self):
        body={"title":"Owner synthetic draft","version":{"body":"Valid synthetic draft"}}
        response=self.client.post("/policies",json=body,headers=self.auth(91002))
        self.assertEqual(response.status_code,201,response.text)
        with self.factory() as db:
            policy=db.get(m.Policy,response.json()["id"])
            self.assertEqual((policy.owner_id,policy.versions[0].created_by),(91002,91002))
        body["title"]="Spoofed author"
        body["version"]["created_by"]=91003
        self.assertEqual(self.client.post("/policies",json=body,headers=self.auth(91002)).status_code,403)

    def test_owner_cannot_publish_or_assign_another_owner(self):
        base={"title":"Synthetic forbidden publication","version":{"body":"Valid synthetic body"}}
        for change in ({"status":"approved"},{"owner_id":91003}):
            self.assertEqual(self.client.post("/policies",json={**base,**change},headers=self.auth(91002)).status_code,403)

    def test_versions_only_assigned_drafts_and_admin_publication(self):
        body={"version_no":"1.1","body":"Valid draft update"}
        self.assertEqual(self.client.post("/policies/95001/versions",json=body,headers=self.auth(91002)).status_code,201)
        self.assertEqual(self.client.post("/policies/95002/versions",json=body,headers=self.auth(91002)).status_code,403)
        self.assertEqual(self.client.patch("/policies/95001/status",json={"status":"approved"},headers=self.auth(91002)).status_code,403)
        response=self.client.patch("/policies/95001/status",json={"status":"approved"},headers=self.auth(91003))
        self.assertEqual(response.status_code,200,response.text)

    def test_private_conversations_no_admin_override(self):
        for uid in (91002,91003,91004):
            self.assertEqual(self.client.get("/conversations/96001",headers=self.auth(uid)).status_code,404)
        self.assertEqual(self.client.get("/conversations/96001",headers=self.auth()).status_code,200)

    def test_clarification_lists_participant_only(self):
        for uid in (91001,91002):
            self.assertEqual([t["id"] for t in self.client.get("/clarifications",headers=self.auth(uid)).json()],[94010])
        self.assertEqual(self.client.get("/clarifications/94010",headers=self.auth(91003)).status_code,404)

    def test_admin_oversight_is_explicit_metadata_only(self):
        self.assertEqual(self.client.get("/admin/clarifications",headers=self.auth(91002)).status_code,403)
        response=self.client.get("/admin/clarifications",headers=self.auth(91003))
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(set(response.json()[0]),{"id","user_id","assigned_to","status","policy_id"})
        self.assertNotIn("Private synthetic",response.text)

    def test_clarification_actor_and_closed_thread_enforcement(self):
        before=self.fixture.counts()
        self.assertEqual(self.client.post("/clarifications/94010/replies",json={"sender_id":91002,"body":"Spoofed reply"},headers=self.auth()).status_code,403)
        self.assertEqual(self.client.post("/clarifications",json={"user_id":91001,"conversation_id":96002},headers=self.auth()).status_code,404)
        self.assertEqual(before,self.fixture.counts())
        with self.factory.begin() as db:
            db.get(m.ClarificationRequest,94010).status="closed"
        self.assertEqual(self.client.post("/clarifications/94010/replies",json={"sender_id":91001,"body":"Cannot reply"},headers=self.auth()).status_code,403)

    def test_participant_reply_and_assignee_resolution(self):
        response=self.client.post("/clarifications/94010/replies",json={"sender_id":91001,"body":"Legitimate reply"},headers=self.auth())
        self.assertEqual(response.status_code,201,response.text)
        self.assertEqual(self.client.post("/clarifications/94010/resolve",headers=self.auth()).status_code,403)
        self.assertEqual(self.client.post("/clarifications/94010/resolve",headers=self.auth(91002)).status_code,200)

    def test_incident_scope_cannot_be_widened_by_query(self):
        self.assertEqual([i["id"] for i in self.client.get("/incidents",headers=self.auth()).json()],[90001])
        self.assertEqual(self.client.get("/incidents?reporter_id=91004",headers=self.auth()).json(),[])
        self.assertEqual(len(self.client.get("/incidents",headers=self.auth(91003)).json()),2)

    def test_incident_handler_cannot_escalate_or_reassign(self):
        for changes in ({"status":"escalated"},{"escalation_level":2},{"assigned_to":91003}):
            self.assertEqual(self.client.patch("/incidents/90001",json=changes,headers=self.auth(91002)).status_code,403)
        self.assertEqual(self.client.patch("/incidents/90001",json={"status":"triaged"},headers=self.auth(91002)).status_code,200)
        self.assertEqual(self.client.patch("/incidents/90001",json={"status":"escalated","escalation_level":2},headers=self.auth(91003)).status_code,200)

    def test_incident_create_as_self_and_no_reporter_impersonation(self):
        before=self.fixture.counts()
        self.assertEqual(self.client.post("/incidents",json={"reporter_id":91002,"description":"Spoofed incident"},headers=self.auth()).status_code,403)
        self.assertEqual(before,self.fixture.counts())
        self.assertEqual(self.client.post("/incidents",json={"reporter_id":91001,"description":"Legitimate incident"},headers=self.auth()).status_code,201)

    def test_feedback_private_and_actor_consistency(self):
        self.assertEqual(self.client.post("/feedback",json={"user_id":91004,"message_id":99001,"rating":True},headers=self.auth(91004)).status_code,404)
        self.assertEqual(self.client.post("/feedback",json={"user_id":91002,"message_id":99001,"rating":True},headers=self.auth()).status_code,403)
        self.assertEqual(self.client.post("/feedback",json={"user_id":91001,"message_id":99001,"rating":True},headers=self.auth()).status_code,201)

    def test_governance_real_aggregate_queries_role_matrix(self):
        self.assertEqual(self.client.get("/dashboard/policy-health",headers=self.auth()).status_code,403)
        for uid in (91002,91003):
            response=self.client.get("/dashboard/policy-health",headers=self.auth(uid))
            self.assertEqual(response.status_code,200,response.text)
            self.assertEqual(response.json()["totals"]["policies"],3)
            self.assertNotIn("Private synthetic",response.text)

    def test_health_is_admin_only_docs_not_public(self):
        self.assertEqual(self.client.get("/health",headers=self.auth()).status_code,403)
        self.assertEqual(self.client.get("/health",headers=self.auth(91003)).status_code,200)
        self.assertEqual(self.client.get("/openapi.json").status_code,404)
        self.assertIn("HTTPBearer",self.app.openapi()["components"]["securitySchemes"])

    def test_protected_pulse_keeps_readonly_feed_contract(self):
        from pulse import service
        old=service._cache
        service._cache={}
        try:
            with patch.object(service,"fetch_source",side_effect=OSError("Synthetic offline feed")):
                response=self.client.get("/api/pulse",headers=self.auth())
            self.assertEqual(response.status_code,200,response.text)
            self.assertIn("articles",response.json())
        finally:
            service._cache=old

    def test_anonymous_denied_before_database_and_safe_outage_errors(self):
        def broken():
            raise RuntimeError("Synthetic private connection detail")
            yield
        self.app.dependency_overrides[main.get_db]=broken
        self.assertEqual(self.client.get("/users").status_code,401)
        response=self.client.get("/users",headers=self.auth())
        self.assertEqual(response.status_code,500)
        self.assertNotIn("connection detail",response.text)

    def test_legacy_ui_not_activated_or_locked_out(self):
        self.assertEqual(self.fixture.client.get("/ui/").status_code,200)
        with patch.dict(os.environ,{"DEREXI_SUBJECT_MAP":""}):
            with self.assertRaises(RuntimeError):
                main.authenticated_application()


class DemoTests(unittest.TestCase):
    # Use only the fixture setup, not the secured suite's tests a second time.
    def setUp(self):
        SecuredTests.setUp(self)
        self.directory=tempfile.TemporaryDirectory(prefix="derexi-demo-test-")
        self.source=Path(self.directory.name)/"approved-synthetic.sqlite"
        raw=self.fixture.engine.raw_connection()
        with sqlite3.connect(self.source) as target:
            raw.driver_connection.backup(target)
        raw.close()
        self.original=self.source.read_bytes()
        self.demo=build_demo(self.source)
        self.local=TestClient(self.demo,base_url="http://127.0.0.1:8000",client=("127.0.0.1",12345),raise_server_exceptions=False)

    def tearDown(self):
        self.local.close()
        self.demo.state.local_engine.dispose()
        self.demo.state.runtime.cleanup()
        self.assertEqual(self.original,self.source.read_bytes(),"Source snapshot was modified")
        self.directory.cleanup()
        SecuredTests.tearDown(self)

    local_db = SecuredTests.local_db

    def login(self):
        key=self.demo.state.activation_key_path.read_text()
        response=self.local.post("/__dev/login",json={"key":key},headers={"Origin":"http://127.0.0.1:8000"})
        self.assertEqual(response.status_code,200,response.text)
        return response.json()

    def test_demo_bootstrap_rotation_and_signed_persona_switch(self):
        session=self.login()
        old_cookie=self.local.cookies.get(COOKIE)
        self.assertIn("HttpOnly",self.local.cookies.jar._cookies['127.0.0.1']['/'][COOKIE]._rest)
        response=self.local.post("/__dev/switch",json={"user_id":91002},headers={"Origin":"http://127.0.0.1:8000","X-CSRF-Token":session['csrf']})
        self.assertEqual(response.status_code,200,response.text)
        self.assertNotEqual(old_cookie,self.local.cookies.get(COOKIE))
        self.assertEqual(self.local.get("/me").json()["role"],"Policy Owner")
        self.assertEqual(self.local.get("/ui/").status_code,200)
        self.assertIn("/__dev/bridge.js",self.local.get("/ui/").text)
        self.assertNotIn("token",response.json())

    def test_demo_requires_activation_origin_and_csrf(self):
        self.assertEqual(self.local.get("/users").status_code,401)
        self.assertEqual(self.local.get("/users",headers={"X-Demo-User-Id":"91003"}).status_code,401)
        session=self.login()
        self.assertEqual(self.local.post("/__dev/switch",json={"user_id":91003}).status_code,403)
        self.assertEqual(self.local.post("/__dev/switch",json={"user_id":91003},headers={"Origin":"http://evil.invalid","X-CSRF-Token":session['csrf']}).status_code,403)

    def test_demo_rejects_remote_clients_and_rebinding(self):
        with TestClient(self.demo,base_url="http://127.0.0.1:8000",client=("198.18.0.1",1234)) as remote:
            self.assertEqual(remote.get("/__dev/login").status_code,403)
        self.assertEqual(self.local.get("/__dev/login",headers={"Host":"evil.invalid"}).status_code,403)

    def test_local_tokens_and_sessions_cannot_authenticate_production(self):
        tokens=[]
        real_encode=jwt.encode
        def capture(*args,**kwargs):
            token=real_encode(*args,**kwargs);tokens.append(token);return token
        with patch("dev_demo.jwt.encode",side_effect=capture):
            self.login()
        self.assertEqual(self.client.get("/users",headers={"Authorization":"Bearer "+tokens[0]}).status_code,401)
        self.client.cookies.set(COOKIE,self.local.cookies.get(COOKIE))
        self.assertEqual(self.client.get("/users").status_code,401)

    def test_demo_refuses_external_or_missing_snapshot(self):
        with self.assertRaises((FileNotFoundError,ValueError)):
            build_demo("postgresql://course.invalid/database")
        with self.assertRaises(ValueError):
            build_demo(self.source,"http://0.0.0.0:8000")

    def test_demo_assistant_writes_only_copy_and_switch_revokes_private_access(self):
        session=self.login()
        headers={"Origin":"http://127.0.0.1:8000","X-CSRF-Token":session['csrf']}
        response=self.local.post("/ask",json={"user_id":91001,"question":"How do I report phishing?"},headers=headers)
        self.assertEqual(response.status_code,200,response.text)
        self.assertFalse(response.json()["needs_clarification"])
        cid=response.json()["conversation_id"]
        self.assertEqual(self.local.get(f"/conversations/{cid}").status_code,200)
        self.assertEqual(self.local.post("/__dev/switch",json={"user_id":91002},headers=headers).status_code,200)
        self.assertEqual(self.local.get(f"/conversations/{cid}").status_code,404)

    def test_demo_activation_is_one_use_and_logout_revokes_session(self):
        key=self.demo.state.activation_key_path.read_text()
        session=self.login()
        self.assertEqual(self.local.post("/__dev/login",json={"key":key},headers={"Origin":"http://127.0.0.1:8000"}).status_code,401)
        response=self.local.post("/__dev/logout",headers={"Origin":"http://127.0.0.1:8000","X-CSRF-Token":session['csrf']})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(self.local.get("/me").status_code,401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
