"""SQLAlchemy ORM models for DeRexi: Policy Pilot.

These models mirror the Supabase schema one-to-one (see
docs/database-design.md). The database already exists, so this module is used
for querying and inserting -- it does not create tables.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


# ---------------------------------------------------------------------------
# Reference domain
# ---------------------------------------------------------------------------
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, server_default=text("''"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    users: Mapped[List["User"]] = relationship(back_populates="department")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, server_default=text("''"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    users: Mapped[List["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    last_name: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True, server_default=text("''"))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    department: Mapped[Optional["Department"]] = relationship(back_populates="users")
    role: Mapped[Optional["Role"]] = relationship(back_populates="users")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


# ---------------------------------------------------------------------------
# Policy Management
# ---------------------------------------------------------------------------
class PolicyCategory(Base):
    __tablename__ = "policy_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, server_default=text("''"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    policies: Mapped[List["Policy"]] = relationship(back_populates="category")


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False, unique=True, server_default=text("''"))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("policy_categories.id"))
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'draft'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    category: Mapped[Optional["PolicyCategory"]] = relationship(back_populates="policies")
    owner: Mapped[Optional["User"]] = relationship(foreign_keys=[owner_id])
    versions: Mapped[List["PolicyVersion"]] = relationship(
        back_populates="policy",
        cascade="all, delete-orphan",
        order_by="PolicyVersion.created_at",
    )


class PolicyVersion(Base):
    __tablename__ = "policy_versions"
    __table_args__ = (UniqueConstraint("policy_id", "version_no"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("policies.id", ondelete="cascade"), nullable=False)
    version_no: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'1.0'"))
    title: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    body: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    effective_date: Mapped[Optional[date]] = mapped_column()
    review_date: Mapped[Optional[date]] = mapped_column()
    requires_review: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    policy: Mapped["Policy"] = relationship(back_populates="versions")
    citations: Mapped[List["PolicyCitation"]] = relationship(back_populates="policy_version")


# ---------------------------------------------------------------------------
# Policy Search & Retrieval
# ---------------------------------------------------------------------------
class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    topic: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'open'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped[Optional["User"]] = relationship(foreign_keys=[user_id])
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="cascade"), nullable=False)
    sender: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    citations: Mapped[List["PolicyCitation"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )


class PolicyCitation(Base):
    __tablename__ = "policy_citations"
    __table_args__ = (UniqueConstraint("message_id", "policy_version_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id", ondelete="cascade"), nullable=False)
    policy_version_id: Mapped[int] = mapped_column(ForeignKey("policy_versions.id"), nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    message: Mapped["Message"] = relationship(back_populates="citations")
    policy_version: Mapped[Optional["PolicyVersion"]] = relationship(back_populates="citations")


# ---------------------------------------------------------------------------
# Clarification & Routing
# ---------------------------------------------------------------------------
class ClarificationRequest(Base):
    __tablename__ = "clarification_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    conversation_id: Mapped[Optional[int]] = mapped_column(ForeignKey("conversations.id", ondelete="set null"))
    message_id: Mapped[Optional[int]] = mapped_column(ForeignKey("messages.id", ondelete="set null"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    policy_id: Mapped[Optional[int]] = mapped_column(ForeignKey("policies.id", ondelete="set null"))
    reason: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'open'"))
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    requester: Mapped[Optional["User"]] = relationship(foreign_keys="ClarificationRequest.user_id")
    assignee: Mapped[Optional["User"]] = relationship(foreign_keys="ClarificationRequest.assigned_to")
    policy: Mapped[Optional["Policy"]] = relationship()
    replies: Mapped[List["ClarificationReply"]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )


class ClarificationReply(Base):
    __tablename__ = "clarification_replies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("clarification_requests.id", ondelete="cascade"), nullable=False
    )
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    request: Mapped["ClarificationRequest"] = relationship(back_populates="replies")
    sender: Mapped[Optional["User"]] = relationship(foreign_keys=[sender_id])


# ---------------------------------------------------------------------------
# Incident Assistance
# ---------------------------------------------------------------------------
class IncidentCategory(Base):
    __tablename__ = "incident_categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, server_default=text("''"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    default_severity: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'medium'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    reports: Mapped[List["IncidentReport"]] = relationship(back_populates="category")


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("incident_categories.id"))
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    severity: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'medium'"))
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'reported'"))
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    escalation_level: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    reporter: Mapped[Optional["User"]] = relationship(foreign_keys="IncidentReport.reporter_id")
    assignee: Mapped[Optional["User"]] = relationship(foreign_keys="IncidentReport.assigned_to")
    category: Mapped[Optional["IncidentCategory"]] = relationship(back_populates="reports")


# ---------------------------------------------------------------------------
# Policy Health Dashboard
# ---------------------------------------------------------------------------
class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    message_id: Mapped[Optional[int]] = mapped_column(ForeignKey("messages.id", ondelete="cascade"))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="set null"))
    rating: Mapped[bool] = mapped_column(Boolean, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    message: Mapped[Optional["Message"]] = relationship()
    user: Mapped[Optional["User"]] = relationship(foreign_keys=[user_id])
