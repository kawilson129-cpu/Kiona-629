"""Pydantic request models for the DeRexi API.

Responses are returned as plain dictionaries built from SQLAlchemy rows, so
only the inbound request bodies need formal models.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator

RecordId = Annotated[int, Field(strict=True, gt=0, le=9_223_372_036_854_775_807)]
Title = Annotated[str, Field(min_length=1, max_length=200)]
Body = Annotated[str, Field(min_length=1, max_length=100_000)]
Version = Annotated[str, Field(min_length=1, max_length=40)]


class RequestModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class PolicyVersionCreate(RequestModel):
    version_no: Version = "1.0"
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    body: Body
    effective_date: Optional[date] = None
    review_date: Optional[date] = None
    requires_review: StrictBool = False
    created_by: Optional[RecordId] = None


class PolicyCreate(RequestModel):
    title: Title
    summary: Optional[str] = Field(default=None, max_length=2000)
    category_id: Optional[RecordId] = None
    owner_id: Optional[RecordId] = None
    status: str = Field(default="draft", pattern="^(draft|in_review|approved|retired)$")
    version: PolicyVersionCreate


class PolicyVersionAdd(RequestModel):
    version_no: Version
    body: Body
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    effective_date: Optional[date] = None
    review_date: Optional[date] = None
    requires_review: StrictBool = False
    created_by: Optional[RecordId] = None


class AskRequest(RequestModel):
    user_id: RecordId
    question: str = Field(min_length=2, max_length=1000)
    topic: Optional[str] = Field(default=None, max_length=1000)


class ClarificationCreate(RequestModel):
    user_id: RecordId
    message_id: Optional[RecordId] = None
    conversation_id: Optional[RecordId] = None
    policy_id: Optional[RecordId] = None
    reason: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    assigned_to: Optional[RecordId] = None


class ClarificationReplyCreate(RequestModel):
    sender_id: RecordId
    body: str = Field(min_length=1, max_length=2000)


class IncidentCreate(RequestModel):
    reporter_id: RecordId
    category_id: Optional[RecordId] = None
    description: str = Field(min_length=2, max_length=10_000)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    assigned_to: Optional[RecordId] = None
    escalation_level: Annotated[int, Field(strict=True, ge=1, le=10)] = 1


class IncidentUpdate(RequestModel):
    status: Optional[str] = Field(default=None, pattern="^(reported|triaged|escalated|resolved)$")
    severity: Optional[str] = Field(default=None, pattern="^(low|medium|high|critical)$")
    assigned_to: Optional[RecordId] = None
    escalation_level: Optional[Annotated[int, Field(strict=True, ge=1, le=10)]] = None
    resolution_notes: Optional[str] = Field(default=None, max_length=10_000)

    @model_validator(mode="after")
    def require_changes(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one incident field to update")
        for field in ("status", "severity", "escalation_level"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError("Status, severity and escalation level cannot be null")
        return self


class FeedbackCreate(RequestModel):
    message_id: RecordId
    user_id: RecordId
    rating: StrictBool
    comment: Optional[str] = Field(default=None, max_length=2000)


class PolicyStatusUpdate(RequestModel):
    status: str = Field(pattern="^(draft|in_review|approved|retired)$")
