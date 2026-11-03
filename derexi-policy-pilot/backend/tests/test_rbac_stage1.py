"""Offline Stage 1 RBAC tests. Run from backend/: python tests/test_rbac_stage1.py.

Only synthetic identities, fresh local signing keys, mocked JWKS, and in-memory
snapshots are used. Never import main/models/database or read backend/.env.
"""

import dataclasses
import os
import sys
import time
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jwt
from cryptography.hazmat.primitives.asymmetric import ec

from auth import AuthenticationError, AuthSettings, SupabaseJWTVerifier
from principals import BusinessUser, PrincipalResolutionError, PrincipalResolver
import rbac as r


def person(uid=91001, role=r.Role.EMPLOYEE):
    return r.Principal(f"synthetic-{uid}", uid, role, 92001, 93001)


class PermissionTests(unittest.TestCase):
    def setUp(self):
        self.employee = person()
        self.owner = person(91002, r.Role.POLICY_OWNER)
        self.admin = person(91003, r.Role.ADMIN)
        self.people = (self.employee, self.owner, self.admin)
        self.thread = r.ClarificationScope(94001, 91001, 91002, "open", 95001)
        self.incident = r.IncidentScope(91001, 91002)

    def test_no_principal_no_permissions(self):
        self.assertFalse(r.can_read_reference(None))
        self.assertFalse(r.actor_matches(None, 91001))
        self.assertFalse(r.can_read_policy(None, r.PolicyScope(91001, "approved")))
        self.assertFalse(r.can_create_policy(None, 91001))
        self.assertFalse(r.can_read_clarification(None, self.thread))
        self.assertIsNone(r.clarification_oversight(None, self.thread))
        self.assertFalse(r.can_read_incident(None, self.incident))
        self.assertFalse(r.can_read_governance(None))

    def test_unknown_or_forged_roles_fail_closed(self):
        for role in (None, "System Administrator", "Developer", 99):
            with self.subTest(role=role):
                p = dataclasses.replace(self.admin, role=role)
                self.assertFalse(r.can_read_reference(p))
                self.assertFalse(r.can_read_governance(p))
                self.assertFalse(r.can_update_incident(p, self.incident, {"status": "resolved"}))

    def test_malformed_principals_fail_closed(self):
        for field, value in (("user_id", True), ("role_id", 0),
                             ("department_id", -1), ("subject", "")):
            self.assertFalse(r.authenticated(dataclasses.replace(self.admin, **{field: value})))

    def test_actor_ids_never_grant_impersonation(self):
        for p in self.people:
            self.assertTrue(r.actor_matches(p, p.user_id))
            for other in (91099, "91001", True, None):
                self.assertFalse(r.actor_matches(p, other))

    def test_reference_and_governance_matrix(self):
        for p in self.people:
            self.assertTrue(r.can_read_reference(p))
            self.assertEqual(r.can_read_governance(p), p is not self.employee)

    def test_approved_policy_readable_by_every_role(self):
        for p in self.people:
            self.assertTrue(r.can_read_policy(p, r.PolicyScope(91099, "approved")))

    def test_nonapproved_policy_read_requires_ownership_or_admin(self):
        for status in ("draft", "in_review", "retired"):
            policy = r.PolicyScope(self.owner.user_id, status)
            self.assertTrue(r.can_read_policy(self.owner, policy))
            self.assertTrue(r.can_read_policy(self.admin, policy))
            self.assertFalse(r.can_read_policy(self.employee, policy))
            self.assertFalse(r.can_read_policy(person(91099, r.Role.POLICY_OWNER), policy))
        self.assertFalse(r.can_read_policy(self.admin, r.PolicyScope(None, "unknown")))

    def test_policy_owner_creates_only_self_owned_draft(self):
        self.assertTrue(r.can_create_policy(self.owner, self.owner.user_id))
        self.assertFalse(r.can_create_policy(self.owner, self.employee.user_id))
        for status in ("in_review", "approved", "retired", "unknown"):
            self.assertFalse(r.can_create_policy(self.owner, self.owner.user_id, status))
        self.assertFalse(r.can_create_policy(self.employee, self.employee.user_id))

    def test_admin_can_create_for_existing_target_id_but_not_invalid_id(self):
        for status in r.POLICY_STATUSES:
            self.assertTrue(r.can_create_policy(self.admin, self.owner.user_id, status))
        for uid in (None, 0, True, "91002"):
            self.assertFalse(r.can_create_policy(self.admin, uid))

    def test_policy_edit_only_assigned_draft_for_owner(self):
        for status in r.POLICY_STATUSES:
            policy = r.PolicyScope(self.owner.user_id, status)
            self.assertEqual(r.can_edit_policy(self.owner, policy), status == "draft")
            self.assertTrue(r.can_edit_policy(self.admin, policy))
            self.assertFalse(r.can_edit_policy(self.employee, policy))
            self.assertFalse(r.can_edit_policy(person(91099, r.Role.POLICY_OWNER), policy))

    def test_initial_approval_publication_and_ownership_are_separate(self):
        policy = r.PolicyScope(self.owner.user_id, "draft")
        self.assertTrue(r.can_edit_policy(self.owner, policy))
        for p in self.people:
            self.assertEqual(r.can_set_policy_status(p, policy, "approved"), p is self.admin)
            self.assertEqual(r.can_set_policy_owner(p, 91099), p is self.admin)
        self.assertFalse(r.can_set_policy_status(self.admin, policy, "invalid"))

    def test_conversations_private_even_for_administrators(self):
        for owner in self.people:
            c = r.ConversationScope(96001, owner.user_id)
            for viewer in self.people:
                self.assertEqual(r.can_read_conversation(viewer, c), owner is viewer)

    def test_clarification_creation_checks_actor_and_linked_records(self):
        c = r.ConversationScope(96001, self.employee.user_id)
        m = r.MessageScope(c.id, "user")
        self.assertTrue(r.can_create_clarification(self.employee, self.employee.user_id, c, m))
        self.assertFalse(r.can_create_clarification(self.admin, self.employee.user_id, c, m))
        self.assertFalse(r.can_create_clarification(self.owner, self.owner.user_id, c))
        self.assertFalse(r.can_create_clarification(self.employee, self.employee.user_id, None, m))
        for bad_message in (r.MessageScope(96099, "user"), r.MessageScope(c.id, "derexi")):
            self.assertFalse(r.can_create_clarification(self.employee, self.employee.user_id, c, bad_message))

    def test_clarification_bodies_participant_only(self):
        self.assertTrue(r.can_read_clarification(self.employee, self.thread))
        self.assertTrue(r.can_read_clarification(self.owner, self.thread))
        self.assertFalse(r.can_read_clarification(self.admin, self.thread))
        self.assertFalse(r.can_read_clarification(person(91099), self.thread))

    def test_explicit_admin_oversight_contains_only_allowlisted_metadata(self):
        overview = r.clarification_oversight(self.admin, self.thread)
        self.assertEqual(dataclasses.asdict(overview), {
            "id": 94001, "user_id": 91001, "assigned_to": 91002,
            "status": "open", "policy_id": 95001,
        })
        self.assertFalse(r.can_read_clarification(self.admin, self.thread))
        for p in (self.employee, self.owner, None):
            self.assertIsNone(r.clarification_oversight(p, self.thread))

    def test_reply_requires_participation_actor_and_open_status(self):
        for status in ("open", "in_progress", "resolved", "closed", "unknown"):
            t = dataclasses.replace(self.thread, status=status)
            for p in self.people:
                expected = p is not self.admin and status in ("open", "in_progress")
                self.assertEqual(r.can_reply_clarification(p, t, p.user_id), expected)
                self.assertFalse(r.can_reply_clarification(p, t, 91099))

    def test_admin_can_reply_if_actual_participant(self):
        t = dataclasses.replace(self.thread, assigned_to=self.admin.user_id)
        self.assertTrue(r.can_reply_clarification(self.admin, t, self.admin.user_id))

    def test_only_assignee_resolves_no_blanket_admin_override(self):
        self.assertTrue(r.can_resolve_clarification(self.owner, self.thread))
        self.assertFalse(r.can_resolve_clarification(self.employee, self.thread))
        self.assertFalse(r.can_resolve_clarification(self.admin, self.thread))
        self.assertFalse(r.can_resolve_clarification(
            self.owner, dataclasses.replace(self.thread, status="resolved")))

    def test_incident_visibility_reporter_assignee_admin_only(self):
        for p in self.people:
            self.assertTrue(r.can_read_incident(p, self.incident))
        self.assertFalse(r.can_read_incident(person(91099, r.Role.POLICY_OWNER), self.incident))

    def test_incident_creation_self_only_without_privileged_fields(self):
        for p in self.people:
            self.assertTrue(r.can_create_incident(p, p.user_id))
            self.assertFalse(r.can_create_incident(p, 91099))
            self.assertFalse(r.can_create_incident(p, p.user_id, assigned_to=91099))
            self.assertFalse(r.can_create_incident(p, p.user_id, escalation_level=2))
            self.assertFalse(r.can_create_incident(p, p.user_id, escalation_level=True))

    def test_assigned_handler_can_triage_but_reporter_cannot(self):
        for changes in ({"status": "triaged"}, {"status": "resolved"},
                        {"severity": "critical", "resolution_notes": "synthetic note"}):
            self.assertTrue(r.can_update_incident(self.owner, self.incident, changes))
            self.assertFalse(r.can_update_incident(self.employee, self.incident, changes))
        # Assignment, not a new role, authorizes ordinary handlers.
        incident = r.IncidentScope(91099, self.employee.user_id)
        self.assertTrue(r.can_update_incident(self.employee, incident, {"status": "triaged"}))

    def test_assignee_cannot_reassign_or_escalate_by_any_supported_field(self):
        for changes in ({"assigned_to": 91099}, {"assigned_to": None},
                        {"assigned_to": self.owner.user_id}, {"escalation_level": 1},
                        {"escalation_level": 2}, {"status": "escalated"},
                        {"status": "escalated", "severity": "low"}):
            self.assertFalse(r.can_update_incident(self.owner, self.incident, changes))
            self.assertTrue(r.can_update_incident(self.admin, self.incident, changes))
        self.assertFalse(r.can_reassign_incident(self.owner))
        self.assertFalse(r.can_escalate_incident(self.owner))

    def test_unknown_incident_fields_and_bad_values_deny_entire_patch(self):
        for changes in ({}, {"reporter_id": 91099}, {"status": "made_up"},
                        {"severity": "made_up"}, {"escalation_level": True},
                        {"assigned_to": "91099"}, {"resolution_notes": []},
                        {"status": "triaged", "role": "System Administrator"}):
            self.assertFalse(r.can_update_incident(self.admin, self.incident, changes))

    def test_feedback_requires_own_assistant_message_and_matching_actor(self):
        c = r.ConversationScope(96001, self.employee.user_id)
        m = r.MessageScope(c.id, "derexi")
        self.assertTrue(r.can_submit_feedback(self.employee, self.employee.user_id, c, m))
        self.assertFalse(r.can_submit_feedback(self.admin, self.admin.user_id, c, m))
        self.assertFalse(r.can_submit_feedback(self.employee, self.owner.user_id, c, m))
        self.assertFalse(r.can_submit_feedback(self.employee, self.employee.user_id, c,
                                             r.MessageScope(96099, "derexi")))
        self.assertFalse(r.can_submit_feedback(self.employee, self.employee.user_id, c,
                                             r.MessageScope(c.id, "user")))

    def test_permission_evaluation_never_mutates_snapshots(self):
        before = dataclasses.asdict(self.owner), dataclasses.asdict(self.thread)
        r.can_reply_clarification(self.owner, self.thread, self.owner.user_id)
        r.can_resolve_clarification(self.owner, self.thread)
        self.assertEqual(before, (dataclasses.asdict(self.owner), dataclasses.asdict(self.thread)))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            self.owner.role = r.Role.ADMIN


class ResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = ec.generate_private_key(ec.SECP256R1())
        cls.other_key = ec.generate_private_key(ec.SECP256R1())

    def setUp(self):
        self.subject = "00000000-0000-4000-8000-000000091001"
        self.user = BusinessUser(91001, 92001, "Employee", 93001)
        self.users = {self.user.id: self.user}
        self.lookup = Mock(side_effect=self.users.get)
        self.keys = Mock()
        self.keys.get_signing_key_from_jwt.return_value = Mock(key=self.key.public_key())
        self.settings = AuthSettings(
            supabase_url="https://synthetic.invalid",
            jwks_url="https://synthetic.invalid/auth/v1/.well-known/jwks.json",
            issuer="https://synthetic.invalid/auth/v1",
        )
        self.verifier = SupabaseJWTVerifier(self.settings, jwk_client=self.keys)
        self.mapping = {self.subject: self.user.id}
        self.resolver = PrincipalResolver(self.verifier, self.mapping, self.lookup)

    def bearer(self, **overrides):
        payload = {"sub": self.subject, "iat": int(time.time()),
                   "exp": int(time.time()) + 3600, "iss": self.settings.issuer,
                   "aud": self.settings.audience}
        payload.update(overrides)
        return "Bearer " + jwt.encode(payload, self.key, algorithm="ES256", headers={"kid": "synthetic"})

    def test_valid_signed_identity_resolves_existing_business_snapshot(self):
        p = self.resolver.resolve(self.bearer())
        self.assertEqual(p, r.Principal(self.subject, 91001, r.Role.EMPLOYEE, 92001, 93001))
        self.lookup.assert_called_once_with(91001)

    def test_forged_business_role_user_and_department_claims_are_ignored(self):
        p = self.resolver.resolve(self.bearer(role="System Administrator", user_id=91099,
                                             role_id=999, department_id=999))
        self.assertEqual(p.role, r.Role.EMPLOYEE)
        self.assertEqual((p.user_id, p.role_id, p.department_id), (91001, 92001, 93001))

    def test_current_server_role_reloaded_each_resolution_without_mutation(self):
        self.assertEqual(self.resolver.resolve(self.bearer()).role, r.Role.EMPLOYEE)
        self.users[91001] = dataclasses.replace(self.user, role_name="Policy Owner")
        self.assertEqual(self.resolver.resolve(self.bearer()).role, r.Role.POLICY_OWNER)
        self.assertEqual(self.user.role_name, "Employee")

    def test_unknown_subject_cannot_link_by_email_or_user_claim(self):
        with self.assertRaises(PrincipalResolutionError):
            self.resolver.resolve(self.bearer(sub="unknown", email="test@synthetic.invalid", user_id=91001))
        self.lookup.assert_not_called()

    def test_missing_business_user_denied_without_account_creation(self):
        self.users.clear()
        with self.assertRaises(PrincipalResolutionError):
            self.resolver.resolve(self.bearer())
        self.assertEqual(self.users, {})

    def test_unknown_role_denied_even_with_admin_token_claim(self):
        for role in ("Developer", "System Admin", "", None):
            self.users[91001] = dataclasses.replace(self.user, role_name=role)
            with self.assertRaises(PrincipalResolutionError):
                self.resolver.resolve(self.bearer(role="System Administrator"))

    def test_inconsistent_business_snapshot_denied(self):
        for changes in ({"id": 91099}, {"role_id": True}, {"department_id": 0}):
            self.users[91001] = dataclasses.replace(self.user, **changes)
            with self.assertRaises(PrincipalResolutionError):
                self.resolver.resolve(self.bearer())

    def test_missing_malformed_or_unsigned_auth_has_no_lookup_or_fallback(self):
        for auth in (None, "", "X-User-ID 91001", "Bearer", "Bearer unsigned",
                     "Bearer " + jwt.encode({"sub": self.subject}, key="", algorithm="none")):
            with self.subTest(auth_type=type(auth).__name__):
                with self.assertRaises(AuthenticationError):
                    self.resolver.resolve(auth)
        self.lookup.assert_not_called()

    def test_expired_wrong_issuer_audience_and_not_yet_valid_denied(self):
        for overrides in ({"exp": int(time.time()) - 60}, {"iss": "https://other.invalid"},
                          {"aud": "other"}, {"nbf": int(time.time()) + 600}, {"sub": ""}):
            with self.assertRaises(AuthenticationError):
                self.resolver.resolve(self.bearer(**overrides))
        self.lookup.assert_not_called()

    def test_wrong_signature_denied_before_lookup(self):
        self.keys.get_signing_key_from_jwt.return_value = Mock(key=self.other_key.public_key())
        with self.assertRaises(AuthenticationError):
            self.resolver.resolve(self.bearer())
        self.lookup.assert_not_called()

    def test_jwks_failure_never_falls_back(self):
        self.keys.get_signing_key_from_jwt.side_effect = OSError("synthetic failure")
        with self.assertRaises(AuthenticationError):
            self.resolver.resolve(self.bearer())
        self.lookup.assert_not_called()

    def test_mapping_invalid_ids_and_many_to_one_rejected(self):
        for mapping in ({"": 91001}, {" padded ": 91001}, {"s": True},
                        {"s": -1}, {"s": "91001"}, {"s": 91001, "t": 91001}):
            with self.assertRaises(ValueError):
                PrincipalResolver(self.verifier, mapping, self.lookup)

    def test_mapping_copied_and_not_mutated(self):
        self.mapping[self.subject] = 91099
        self.assertEqual(self.resolver.resolve(self.bearer()).user_id, 91001)
        self.assertEqual(self.mapping[self.subject], 91099)

    def test_empty_mapping_fails_closed(self):
        resolver = PrincipalResolver(self.verifier, {}, self.lookup)
        with self.assertRaises(PrincipalResolutionError):
            resolver.resolve(self.bearer())
        self.lookup.assert_not_called()

    def test_no_network_or_database_access_for_isolated_resolution(self):
        with patch("socket.socket.connect", side_effect=AssertionError("network forbidden")):
            self.assertEqual(self.resolver.resolve(self.bearer()).user_id, 91001)
        self.assertNotIn("database", sys.modules)
        self.assertNotIn("models", sys.modules)
        self.assertNotIn("main", sys.modules)


if __name__ == "__main__":
    unittest.main(verbosity=2)
