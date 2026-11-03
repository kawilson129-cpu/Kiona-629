"""Stage 1 permission rules: immutable snapshots, no database or HTTP imports.

These rules are NOT installed on application routes. Snapshots must come from a
trusted server data source, never directly from a request body or JWT role claim.
Developer tooling/OS access grants no application privilege here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class Role(str, Enum):
    EMPLOYEE = "Employee"
    POLICY_OWNER = "Policy Owner"
    ADMIN = "System Administrator"


def valid_id(value: object) -> bool:
    return type(value) is int and value > 0


@dataclass(frozen=True)
class Principal:
    subject: str
    user_id: int
    role: Role
    role_id: int
    department_id: int


@dataclass(frozen=True)
class PolicyScope:
    owner_id: int | None
    status: str


@dataclass(frozen=True)
class ConversationScope:
    id: int
    user_id: int


@dataclass(frozen=True)
class MessageScope:
    conversation_id: int
    sender: str


@dataclass(frozen=True)
class ClarificationScope:
    id: int
    user_id: int
    assigned_to: int | None
    status: str
    policy_id: int | None = None


@dataclass(frozen=True)
class IncidentScope:
    reporter_id: int
    assigned_to: int | None


@dataclass(frozen=True)
class ClarificationOversight:
    """Explicit administrative projection: no question, reason or reply bodies."""

    id: int
    user_id: int
    assigned_to: int | None
    status: str
    policy_id: int | None


POLICY_STATUSES = frozenset({"draft", "in_review", "approved", "retired"})
OPEN_THREADS = frozenset({"open", "in_progress"})
INCIDENT_STATUSES = frozenset({"reported", "triaged", "escalated", "resolved"})
SEVERITIES = frozenset({"low", "medium", "high", "critical"})


def authenticated(principal: Principal | None) -> bool:
    return (
        isinstance(principal, Principal)
        and isinstance(principal.subject, str)
        and bool(principal.subject.strip())
        and isinstance(principal.role, Role)
        and all(valid_id(v) for v in (
            principal.user_id, principal.role_id, principal.department_id
        ))
    )


def is_admin(principal: Principal | None) -> bool:
    return authenticated(principal) and principal.role is Role.ADMIN


def actor_matches(principal: Principal | None, actor_id: int) -> bool:
    """Compatibility assertion for body/query actor IDs; never impersonation."""
    return authenticated(principal) and valid_id(actor_id) and principal.user_id == actor_id


def can_read_reference(principal: Principal | None) -> bool:
    """Reference data, minimal employee directory, approved search and Pulse."""
    return authenticated(principal)


def can_read_policy(principal: Principal | None, policy: PolicyScope) -> bool:
    return authenticated(principal) and policy.status in POLICY_STATUSES and (
        policy.status == "approved"
        or is_admin(principal)
        or (principal.role is Role.POLICY_OWNER and policy.owner_id == principal.user_id)
    )


def can_create_policy(
    principal: Principal | None, owner_id: int, status: str = "draft"
) -> bool:
    # Target existence must also be checked by the future data adapter.
    return authenticated(principal) and valid_id(owner_id) and status in POLICY_STATUSES and (
        is_admin(principal)
        or (principal.role is Role.POLICY_OWNER
            and owner_id == principal.user_id and status == "draft")
    )


def can_edit_policy(principal: Principal | None, policy: PolicyScope) -> bool:
    """Content/version editing only; does not grant approval or owner changes."""
    return authenticated(principal) and policy.status in POLICY_STATUSES and (
        is_admin(principal)
        or (principal.role is Role.POLICY_OWNER
            and policy.owner_id == principal.user_id and policy.status == "draft")
    )


def can_set_policy_status(
    principal: Principal | None, policy: PolicyScope, status: str
) -> bool:
    # Keep publication and content permissions separate, including initial approval.
    return is_admin(principal) and policy.status in POLICY_STATUSES and status in POLICY_STATUSES


def can_set_policy_owner(principal: Principal | None, owner_id: int) -> bool:
    return is_admin(principal) and valid_id(owner_id)


def can_read_conversation(
    principal: Principal | None, conversation: ConversationScope
) -> bool:
    # Current conversations have one employee participant; admins have no override.
    return valid_id(conversation.id) and actor_matches(principal, conversation.user_id)


def can_create_clarification(
    principal: Principal | None,
    requester_id: int,
    conversation: ConversationScope | None = None,
    message: MessageScope | None = None,
) -> bool:
    if not actor_matches(principal, requester_id):
        return False
    if conversation is not None and not can_read_conversation(principal, conversation):
        return False
    if message is not None:
        return (conversation is not None and message.conversation_id == conversation.id
                and message.sender == "user")
    return True


def can_read_clarification(
    principal: Principal | None, thread: ClarificationScope
) -> bool:
    return authenticated(principal) and valid_id(thread.id) and principal.user_id in (
        thread.user_id, thread.assigned_to
    )


def clarification_oversight(
    principal: Principal | None, thread: ClarificationScope
) -> ClarificationOversight | None:
    """Separate metadata-only admin operation; never unlocks private content."""
    if not is_admin(principal) or not valid_id(thread.id):
        return None
    return ClarificationOversight(
        thread.id, thread.user_id, thread.assigned_to, thread.status, thread.policy_id
    )


def can_reply_clarification(
    principal: Principal | None, thread: ClarificationScope, sender_id: int
) -> bool:
    return (can_read_clarification(principal, thread)
            and actor_matches(principal, sender_id) and thread.status in OPEN_THREADS)


def can_resolve_clarification(
    principal: Principal | None, thread: ClarificationScope
) -> bool:
    # Administrative oversight alone is not participation or resolution authority.
    return (actor_matches(principal, thread.assigned_to)
            and thread.status in OPEN_THREADS and valid_id(thread.id))


def can_read_incident(principal: Principal | None, incident: IncidentScope) -> bool:
    return authenticated(principal) and (
        is_admin(principal)
        or principal.user_id in (incident.reporter_id, incident.assigned_to)
    )


def can_create_incident(
    principal: Principal | None, reporter_id: int,
    assigned_to: int | None = None, escalation_level: int = 1,
) -> bool:
    # Assignment/escalation are separate triage operations, including for admins.
    return (actor_matches(principal, reporter_id) and assigned_to is None
            and type(escalation_level) is int and escalation_level == 1)


def can_reassign_incident(principal: Principal | None) -> bool:
    return is_admin(principal)


def can_escalate_incident(principal: Principal | None) -> bool:
    return is_admin(principal)


def can_update_incident(
    principal: Principal | None, incident: IncidentScope, changes: Mapping[str, object]
) -> bool:
    if not authenticated(principal) or not changes:
        return False
    if not (is_admin(principal) or principal.user_id == incident.assigned_to):
        return False
    allowed = {"status", "severity", "resolution_notes", "assigned_to", "escalation_level"}
    if set(changes) - allowed:
        return False
    if "assigned_to" in changes:
        target = changes["assigned_to"]
        if not can_reassign_incident(principal) or (target is not None and not valid_id(target)):
            return False
    if "escalation_level" in changes:
        if not can_escalate_incident(principal) or not valid_id(changes["escalation_level"]):
            return False
    if "status" in changes:
        status = changes["status"]
        if not isinstance(status, str) or status not in INCIDENT_STATUSES:
            return False
        if status == "escalated" and not can_escalate_incident(principal):
            return False
    if "severity" in changes:
        severity = changes["severity"]
        if not isinstance(severity, str) or severity not in SEVERITIES:
            return False
    if "resolution_notes" in changes and not isinstance(changes["resolution_notes"], (str, type(None))):
        return False
    return True


def can_submit_feedback(
    principal: Principal | None, actor_id: int,
    conversation: ConversationScope, message: MessageScope,
) -> bool:
    return (actor_matches(principal, actor_id)
            and can_read_conversation(principal, conversation)
            and message.conversation_id == conversation.id and message.sender == "derexi")


def can_read_governance(principal: Principal | None) -> bool:
    """Aggregates only; no implicit conversation/thread-body access."""
    return authenticated(principal) and principal.role in (Role.POLICY_OWNER, Role.ADMIN)
