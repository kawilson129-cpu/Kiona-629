"""Pydantic request models for the DeRexi API.

Responses are returned as plain dictionaries built from SQLAlchemy rows, so
only the inbound request bodies need formal models.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class PolicyVersionCreate(BaseModel):
    version_no: str = "1.0"
    title: Optional[str] = None
    body: str
    effective_date: Optional[date] = None
    review_date: Optional[date] = None
    requires_review: bool = False
    created_by: Optional[int] = None


class PolicyCreate(BaseModel):
    title: str
    summary: Optional[str] = None
    category_id: Optional[int] = None
    owner_id: Optional[int] = None
    status: str = Field(default="draft", pattern="^(draft|in_review|approved|retired)$")
    version: PolicyVersionCreate


class PolicyVersionAdd(BaseModel):
    version_no: str
    body: str
    title: Optional[str] = None
    effective_date: Optional[date] = None
    review_date: Optional[date] = None
    requires_review: bool = False
    created_by: Optional[int] = None


class AskRequest(BaseModel):
    user_id: int
    question: str = Field(min_length=2)
    topic: Optional[str] = None


class ClarificationCreate(BaseModel):
    user_id: int
    message_id: Optional[int] = None
    conversation_id: Optional[int] = None
    policy_id: Optional[int] = None
    reason: Optional[str] = None
    assigned_to: Optional[int] = None


class ClarificationReplyCreate(BaseModel):
    sender_id: int
    body: str = Field(min_length=1)


class IncidentCreate(BaseModel):
    reporter_id: int
    category_id: Optional[int] = None
    description: str = Field(min_length=2)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    assigned_to: Optional[int] = None
    escalation_level: int = 1


class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(default=None, pattern="^(reported|triaged|escalated|resolved)$")
    severity: Optional[str] = Field(default=None, pattern="^(low|medium|high|critical)$")
    assigned_to: Optional[int] = None
    escalation_level: Optional[int] = None
    resolution_notes: Optional[str] = None


class FeedbackCreate(BaseModel):
    message_id: int
    user_id: int
    rating: bool
    comment: Optional[str] = None
