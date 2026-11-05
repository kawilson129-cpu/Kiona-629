"""Pydantic request models for the DeRexi API.

Responses are returned as plain dictionaries built from SQLAlchemy rows, so
only the inbound request bodies need formal models.

Week 7 note: identity fields (``user_id``, ``sender_id``, ``reporter_id``) are
kept as optional legacy fields for backwards compatibility, but every message
route derives the actor from the verified bearer token. A supplied id that
contradicts the token is rejected with 403 rather than silently ignored.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, StrictBool


class PolicyVersionCreate(BaseModel):
    version_no: str = "1.0"
    title: Optional[str] = Field(default=None, max_length=200)
    body: str = Field(min_length=1, max_length=20_000)
    effective_date: Optional[date] = None
    review_date: Optional[date] = None
    requires_review: bool = False
    created_by: Optional[int] = None


class PolicyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: Optional[str] = Field(default=None, max_length=1_000)
    category_id: Optional[int] = None
    owner_id: Optional[int] = None
    status: str = Field(default="draft", pattern="^(draft|in_review|approved|retired)$")
    version: PolicyVersionCreate


class PolicyVersionAdd(BaseModel):
    version_no: str = Field(min_length=1, max_length=20)
    body: str = Field(min_length=1, max_length=20_000)
    title: Optional[str] = Field(default=None, max_length=200)
    effective_date: Optional[date] = None
    review_date: Optional[date] = None
    requires_review: bool = False
    created_by: Optional[int] = None


class AskRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    # ``user_id`` is accepted only so older clients do not break. The server
    # always uses the authenticated identity and 403s on a mismatch.
    user_id: Optional[int] = None
    question: str = Field(min_length=2, max_length=1000)
    topic: Optional[str] = Field(default=None, max_length=1000)


class ClarificationCreate(BaseModel):
    """Create a clarification thread from a Policy Assistant answer.

    ``conversation_id`` is required. ``policy_id`` must be one of the policies
    cited in that conversation. ``context`` is the employee's added detail.
    Legacy fields are optional; the server validates them against the answer.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    conversation_id: Optional[int] = None
    message_id: Optional[int] = None
    policy_id: Optional[int] = None
    context: Optional[str] = Field(default=None, min_length=2, max_length=2000)
    reason: Optional[str] = Field(default=None, min_length=2, max_length=2000)
    user_id: Optional[int] = None
    assigned_to: Optional[int] = None


class ClarificationReplyCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    body: str = Field(min_length=1, max_length=4000)
    # Legacy: ignored. The sender is the authenticated user.
    sender_id: Optional[int] = None


class ClarificationReopen(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    reason: Optional[str] = Field(default=None, max_length=2000)


class ClarificationAssign(BaseModel):
    assignee_id: int


class IncidentCreate(BaseModel):
    reporter_id: Optional[int] = None
    category_id: Optional[int] = None
    description: str = Field(min_length=2, max_length=4000)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    assigned_to: Optional[int] = None
    escalation_level: int = 1


class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(default=None, pattern="^(reported|triaged|escalated|resolved)$")
    severity: Optional[str] = Field(default=None, pattern="^(low|medium|high|critical)$")
    assigned_to: Optional[int] = None
    escalation_level: Optional[int] = None
    resolution_notes: Optional[str] = Field(default=None, max_length=4000)


class FeedbackCreate(BaseModel):
    message_id: int
    # Legacy: ignored. Feedback is attributed to the authenticated user.
    user_id: Optional[int] = None
    rating: StrictBool
    comment: Optional[str] = Field(default=None, max_length=2000)
