"""DeRexi: Policy Pilot -- FastAPI backend.

Implements the five MVP components against the Supabase Postgres schema:
  1. Policy Management
  2. Policy Search & Retrieval
  3. Clarification & Routing
  4. Incident Assistance
  5. Policy Health Dashboard

Run locally:
    uvicorn main:app --reload
from the backend/ directory, with DATABASE_URL set in backend/.env.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, text
from sqlalchemy.orm import Session

import ai
import schemas
from database import get_db
from models import (
    ClarificationReply,
    ClarificationRequest,
    Conversation,
    Department,
    Feedback,
    IncidentCategory,
    IncidentReport,
    Message,
    Policy,
    PolicyCitation,
    PolicyVersion,
    Role,
    User,
)

# Minimum blended similarity score before DeRexi treats a match as authoritative.
# Calibrated against the seeded handbook: genuine matches score >= 0.27, while
# questions with no matching approved policy (e.g. wire approval thresholds)
# score ~0.17 and are routed to a policy owner instead of answered.
CONFIDENCE_THRESHOLD = 0.22

app = FastAPI(
    title="DeRexi: Policy Pilot API",
    description="Policy governance and incident assistance for Aurum Capital Bank.",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Employee UI (Week 6): vanilla HTML/CSS/JS served at /ui.
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/ui", StaticFiles(directory=STATIC_DIR, html=True), name="ui")


# ---------------------------------------------------------------------------
# Search / helpers
# ---------------------------------------------------------------------------
SEARCH_SQL = text(
    """
    WITH current_versions AS (
        SELECT DISTINCT ON (pv.policy_id)
               pv.id AS policy_version_id,
               pv.policy_id,
               pv.title,
               pv.version_no,
               pv.body
        FROM policy_versions pv
        ORDER BY pv.policy_id, pv.created_at DESC, pv.id DESC
    )
    SELECT cv.policy_id,
           p.title,
           p.summary,
           cv.policy_version_id,
           cv.version_no,
           cv.body,
           (0.6 * extensions.word_similarity(:q, cv.body)
            + 0.4 * extensions.similarity(cv.title, :q)) AS score
    FROM current_versions cv
    JOIN policies p ON p.id = cv.policy_id
    WHERE p.status = 'approved'
    ORDER BY score DESC
    LIMIT :limit
    """
)


def make_excerpt(body: str, question: str, length: int = 260) -> str:
    """Return the policy sentence most relevant to the question."""
    body = " ".join(body.split())
    sentences = re.split(r"(?<=[.!?])\s+", body)
    keywords = {w for w in re.findall(r"[a-z]{4,}", question.lower())}
    for sentence in sentences:
        if keywords & set(re.findall(r"[a-z]{4,}", sentence.lower())):
            return sentence if len(sentence) <= length else sentence[:length].rstrip() + "..."
    return body[:length].rstrip() + ("..." if len(body) > length else "")


# Function words and institution vocabulary that must not, on their own, count
# as evidence a policy answers a question.
GENERIC_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "if", "but", "of", "to", "for", "with",
    "from", "by", "in", "on", "at", "is", "are", "was", "were", "am", "be",
    "been", "being", "do", "does", "did", "doing", "what", "when", "where",
    "which", "why", "how", "who", "whom", "whose", "can", "could", "will",
    "would", "should", "shall", "may", "might", "must", "that", "this",
    "these", "those", "there", "here", "not", "no", "yes", "all", "any",
    "some", "each", "every", "you", "your", "yours", "we", "our", "ours",
    "i", "me", "my", "he", "him", "she", "her", "it", "its", "they", "them",
    "their", "us", "have", "has", "had", "get", "got", "make", "about",
    "into", "over", "under", "please", "want", "need", "know", "tell", "ask",
    "policy", "policies", "rule", "rules", "law", "laws", "regulation",
    "bank", "banks", "company", "companies", "organization", "employee",
    "employees", "staff", "person", "people", "aurum", "capital",
})


def substantive_keywords(question: str) -> list:
    """Return the question's substantive tokens (generic words removed)."""
    words = re.findall(r"[a-z]{4,}", question.lower())
    return sorted({w for w in words if w not in GENERIC_STOPWORDS})


def contains_keyword(haystack: str, keywords: list) -> bool:
    """True if any keyword (or its singular form) appears in the haystack."""
    for keyword in keywords:
        if keyword in haystack:
            return True
        if keyword.endswith("s") and keyword[:-1] in haystack:
            return True
    return False


def make_guidance(body: str, question: str, max_length: int = 240) -> str:
    """Return the single policy sentence that best addresses the question."""
    body = " ".join(body.split())
    sentences = re.split(r"(?<=[.!?])\s+", body)
    keywords = set(substantive_keywords(question))
    best, best_hits = None, 0
    for sentence in sentences:
        if len(sentence) < 20:
            continue
        hits = len(keywords & set(re.findall(r"[a-z]{4,}", sentence.lower())))
        if best is None or hits > best_hits:
            best, best_hits = sentence, hits
    if best is None:
        best = sentences[0] if sentences else body
    if len(best) > max_length:
        best = best[:max_length].rstrip() + "..."
    return best


def policy_to_dict(policy: Policy, db: Session) -> dict:
    latest = (
        db.query(PolicyVersion)
        .filter(PolicyVersion.policy_id == policy.id)
        .order_by(PolicyVersion.created_at.desc(), PolicyVersion.id.desc())
        .first()
    )
    return {
        "id": policy.id,
        "title": policy.title,
        "summary": policy.summary,
        "status": policy.status,
        "category_id": policy.category_id,
        "category": policy.category.name if policy.category else None,
        "owner_id": policy.owner_id,
        "owner": policy.owner.full_name if policy.owner else None,
        "latest_version": latest.version_no if latest else None,
        "review_date": latest.review_date.isoformat() if latest and latest.review_date else None,
        "requires_review": bool(latest.requires_review) if latest else False,
        "created_at": policy.created_at.isoformat() if policy.created_at else None,
        "updated_at": policy.updated_at.isoformat() if policy.updated_at else None,
    }


# ---------------------------------------------------------------------------
# Service metadata
# ---------------------------------------------------------------------------
@app.get("/")
def root() -> dict:
    return {
        "service": "DeRexi: Policy Pilot API",
        "version": "0.4.0",
        "institution": "Aurum Capital Bank",
        "docs": "/docs",
    }


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    db.execute(text("select 1"))
    return {"status": "ok", "database": "reachable"}


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
@app.get("/departments")
def list_departments(db: Session = Depends(get_db)) -> list:
    return [
        {"id": d.id, "name": d.name}
        for d in db.query(Department).order_by(Department.id).all()
    ]


@app.get("/roles")
def list_roles(db: Session = Depends(get_db)) -> list:
    return [{"id": r.id, "name": r.name} for r in db.query(Role).order_by(Role.id).all()]


@app.get("/categories")
def list_policy_categories(db: Session = Depends(get_db)) -> list:
    rows = db.execute(
        text(
            """
            SELECT c.id, c.name, count(p.id) AS count
            FROM policy_categories c
            LEFT JOIN policies p ON p.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY c.id
            """
        )
    ).mappings().all()
    return [{"id": r["id"], "name": r["name"], "count": r["count"]} for r in rows]


@app.get("/users")
def list_users(db: Session = Depends(get_db)) -> list:
    users = db.query(User).order_by(User.id).all()
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "department_id": u.department_id,
            "department": u.department.name if u.department else None,
            "role_id": u.role_id,
            "role": u.role.name if u.role else None,
        }
        for u in users
    ]


# ---------------------------------------------------------------------------
# 1. Policy Management
# ---------------------------------------------------------------------------
@app.get("/policies")
def list_policies(
    status: Optional[str] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
) -> list:
    query = db.query(Policy)
    if status:
        query = query.filter(Policy.status == status)
    if category_id:
        query = query.filter(Policy.category_id == category_id)
    return [policy_to_dict(p, db) for p in query.order_by(Policy.id).all()]


@app.get("/policies/search")
def search_policies(
    q: str = Query(min_length=2),
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> list:
    rows = db.execute(SEARCH_SQL, {"q": q, "limit": limit}).mappings().all()
    return [
        {
            "policy_id": row["policy_id"],
            "policy_version_id": row["policy_version_id"],
            "title": row["title"],
            "version_no": row["version_no"],
            "score": round(float(row["score"]), 4),
            "excerpt": make_excerpt(row["body"], q),
        }
        for row in rows
    ]


@app.get("/policies/{policy_id}")
def get_policy(policy_id: int, db: Session = Depends(get_db)) -> dict:
    policy = db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    result = policy_to_dict(policy, db)
    result["versions"] = [
        {
            "id": v.id,
            "version_no": v.version_no,
            "title": v.title,
            "body": v.body,
            "effective_date": v.effective_date.isoformat() if v.effective_date else None,
            "review_date": v.review_date.isoformat() if v.review_date else None,
            "requires_review": v.requires_review,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in policy.versions
    ]
    return result


@app.post("/policies", status_code=201)
def create_policy(payload: schemas.PolicyCreate, db: Session = Depends(get_db)) -> dict:
    if db.query(Policy).filter(Policy.title == payload.title).first():
        raise HTTPException(status_code=409, detail="A policy with that title already exists")
    policy = Policy(
        title=payload.title,
        summary=payload.summary,
        category_id=payload.category_id,
        owner_id=payload.owner_id,
        status=payload.status,
    )
    db.add(policy)
    db.flush()

    v = payload.version
    version = PolicyVersion(
        policy_id=policy.id,
        version_no=v.version_no,
        title=v.title or policy.title,
        body=v.body,
        effective_date=v.effective_date,
        review_date=v.review_date,
        requires_review=v.requires_review,
        created_by=v.created_by,
    )
    db.add(version)
    db.commit()
    return policy_to_dict(policy, db)


@app.post("/policies/{policy_id}/versions", status_code=201)
def add_policy_version(
    policy_id: int, payload: schemas.PolicyVersionAdd, db: Session = Depends(get_db)
) -> dict:
    policy = db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    exists = (
        db.query(PolicyVersion)
        .filter(PolicyVersion.policy_id == policy_id, PolicyVersion.version_no == payload.version_no)
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="That version number already exists for this policy")

    version = PolicyVersion(
        policy_id=policy_id,
        version_no=payload.version_no,
        title=payload.title or policy.title,
        body=payload.body,
        effective_date=payload.effective_date,
        review_date=payload.review_date,
        requires_review=payload.requires_review,
        created_by=payload.created_by,
    )
    db.add(version)
    policy.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {
        "policy_id": policy_id,
        "version_no": version.version_no,
        "created_at": version.created_at.isoformat() if version.created_at else None,
    }


# ---------------------------------------------------------------------------
# 2. Policy Search & Retrieval -- the ask workflow
# ---------------------------------------------------------------------------
@app.post("/ask")
def ask(payload: schemas.AskRequest, db: Session = Depends(get_db)) -> dict:
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    question = payload.question.strip()

    conversation = Conversation(
        user_id=user.id,
        topic=payload.topic or question[:120],
        status="open",
    )
    db.add(conversation)
    db.flush()

    user_message = Message(conversation_id=conversation.id, sender="user", body=question)
    db.add(user_message)
    db.flush()

    results = db.execute(SEARCH_SQL, {"q": question, "limit": 3}).mappings().all()
    top_score = float(results[0]["score"]) if results else 0.0
    top = results[0] if results else None
    confident = bool(results) and top_score >= CONFIDENCE_THRESHOLD
    if confident:
        haystack = " ".join([top["title"], top["body"]]).lower()
        keywords = substantive_keywords(question)
        confident = bool(keywords) and contains_keyword(haystack, keywords)

    if confident:
        context = [
            {"title": row["title"], "version_no": row["version_no"], "body": row["body"]}
            for row in results[:3]
            if float(row["score"]) >= CONFIDENCE_THRESHOLD
        ]
        llm_answer = ai.generate_answer(question, context) if context else None
        if llm_answer:
            answer = f"{llm_answer}\nReference: {top['title']} (v{top['version_no']})"
        else:
            guidance = make_guidance(top["body"], question)
            answer = (
                f"Here's what you should do: {guidance}"
                f"\nReference: {top['title']} (v{top['version_no']}) — review the "
                "full policy for complete guidance."
            )
        derexi_message = Message(conversation_id=conversation.id, sender="derexi", body=answer)
        db.add(derexi_message)
        db.flush()

        citations = []
        for row in results:
            if float(row["score"]) < CONFIDENCE_THRESHOLD:
                continue
            row_excerpt = make_excerpt(row["body"], question)
            db.add(
                PolicyCitation(
                    message_id=derexi_message.id,
                    policy_version_id=row["policy_version_id"],
                    excerpt=row_excerpt,
                )
            )
            citations.append(
                {
                    "policy_id": row["policy_id"],
                    "policy_version_id": row["policy_version_id"],
                    "title": row["title"],
                    "version_no": row["version_no"],
                    "score": round(float(row["score"]), 4),
                    "excerpt": row_excerpt,
                }
            )

        db.commit()
        return {
            "conversation_id": conversation.id,
            "user_message_id": user_message.id,
            "derexi_message_id": derexi_message.id,
            "answer": answer,
            "citations": citations,
            "needs_clarification": False,
            "confidence": round(top_score, 4),
        }

    # Not confident -- route to a policy owner instead of guessing.
    policy_id = results[0]["policy_id"] if results else None
    assignee = None
    if policy_id:
        assignee = db.execute(
            text("select owner_id from policies where id = :pid"), {"pid": policy_id}
        ).scalar()
    if assignee is None:
        assignee = db.execute(
            text(
                """
                select u.id
                from users u
                join roles r on r.id = u.role_id
                where r.name = 'Policy Owner'
                order by u.id
                limit 1
                """
            )
        ).scalar()

    answer = (
        "The policy library does not contain enough information to answer this "
        "confidently, so I have routed it to a policy owner for clarification "
        "rather than guess."
    )
    derexi_message = Message(conversation_id=conversation.id, sender="derexi", body=answer)
    db.add(derexi_message)
    db.flush()

    request = ClarificationRequest(
        conversation_id=conversation.id,
        message_id=user_message.id,
        user_id=user.id,
        policy_id=policy_id,
        reason="No approved policy confidently matched the question.",
        status="open",
        assigned_to=assignee,
    )
    db.add(request)
    db.commit()

    return {
        "conversation_id": conversation.id,
        "user_message_id": user_message.id,
        "derexi_message_id": derexi_message.id,
        "answer": answer,
        "citations": [],
        "needs_clarification": True,
        "clarification_request_id": request.id,
        "assigned_to": assignee,
        "confidence": round(top_score, 4),
    }


@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, db: Session = Depends(get_db)) -> dict:
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = []
    for message in conversation.messages:
        citations = []
        for citation in message.citations:
            pv = citation.policy_version
            citations.append(
                {
                    "policy_id": pv.policy_id if pv else None,
                    "policy_version_id": citation.policy_version_id,
                    "title": pv.title if pv else None,
                    "version_no": pv.version_no if pv else None,
                    "excerpt": citation.excerpt,
                }
            )
        messages.append(
            {
                "id": message.id,
                "sender": message.sender,
                "body": message.body,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "citations": citations,
            }
        )

    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "topic": conversation.topic,
        "status": conversation.status,
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
        "messages": messages,
    }


# ---------------------------------------------------------------------------
# 3. Clarification & Routing
# ---------------------------------------------------------------------------
@app.get("/clarifications")
def list_clarifications(
    status: Optional[str] = Query(default=None),
    assigned_to: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
) -> list:
    query = db.query(ClarificationRequest)
    if status:
        query = query.filter(ClarificationRequest.status == status)
    if assigned_to:
        query = query.filter(ClarificationRequest.assigned_to == assigned_to)

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "requester": r.requester.full_name if r.requester else None,
            "policy_id": r.policy_id,
            "reason": r.reason,
            "status": r.status,
            "assigned_to": r.assigned_to,
            "assignee": r.assignee.full_name if r.assignee else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
        }
        for r in query.order_by(ClarificationRequest.created_at.desc()).all()
    ]


@app.post("/clarifications", status_code=201)
def create_clarification(payload: schemas.ClarificationCreate, db: Session = Depends(get_db)) -> dict:
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    request = ClarificationRequest(**payload.model_dump())
    db.add(request)
    db.commit()
    return {"id": request.id, "status": request.status, "assigned_to": request.assigned_to}


@app.get("/clarifications/{request_id}")
def get_clarification(request_id: int, db: Session = Depends(get_db)) -> dict:
    request = db.get(ClarificationRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Clarification request not found")
    return {
        "id": request.id,
        "user_id": request.user_id,
        "requester": request.requester.full_name if request.requester else None,
        "policy_id": request.policy_id,
        "reason": request.reason,
        "status": request.status,
        "assigned_to": request.assigned_to,
        "assignee": request.assignee.full_name if request.assignee else None,
        "created_at": request.created_at.isoformat() if request.created_at else None,
        "resolved_at": request.resolved_at.isoformat() if request.resolved_at else None,
        "replies": [
            {
                "id": reply.id,
                "sender_id": reply.sender_id,
                "sender": reply.sender.full_name if reply.sender else None,
                "body": reply.body,
                "created_at": reply.created_at.isoformat() if reply.created_at else None,
            }
            for reply in request.replies
        ],
    }


@app.post("/clarifications/{request_id}/replies", status_code=201)
def add_clarification_reply(
    request_id: int, payload: schemas.ClarificationReplyCreate, db: Session = Depends(get_db)
) -> dict:
    request = db.get(ClarificationRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Clarification request not found")
    if not db.get(User, payload.sender_id):
        raise HTTPException(status_code=404, detail="Sender not found")

    reply = ClarificationReply(
        request_id=request_id, sender_id=payload.sender_id, body=payload.body
    )
    db.add(reply)
    if request.status == "open":
        request.status = "in_progress"
    db.commit()
    return {"id": reply.id, "request_id": request_id, "status": request.status}


@app.post("/clarifications/{request_id}/resolve")
def resolve_clarification(request_id: int, db: Session = Depends(get_db)) -> dict:
    request = db.get(ClarificationRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Clarification request not found")
    request.status = "resolved"
    request.resolved_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": request.id, "status": request.status, "resolved_at": request.resolved_at.isoformat()}


# ---------------------------------------------------------------------------
# 4. Incident Assistance
# ---------------------------------------------------------------------------
@app.get("/incident-categories")
def list_incident_categories(db: Session = Depends(get_db)) -> list:
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "default_severity": c.default_severity,
        }
        for c in db.query(IncidentCategory).order_by(IncidentCategory.id).all()
    ]


@app.get("/incidents")
def list_incidents(
    status: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> list:
    query = db.query(IncidentReport)
    if status:
        query = query.filter(IncidentReport.status == status)
    if severity:
        query = query.filter(IncidentReport.severity == severity)
    return [_incident_dict(i) for i in query.order_by(IncidentReport.created_at.desc()).all()]


def _incident_dict(incident: IncidentReport) -> dict:
    return {
        "id": incident.id,
        "reporter_id": incident.reporter_id,
        "reporter": incident.reporter.full_name if incident.reporter else None,
        "category_id": incident.category_id,
        "category": incident.category.name if incident.category else None,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "assigned_to": incident.assigned_to,
        "assignee": incident.assignee.full_name if incident.assignee else None,
        "escalation_level": incident.escalation_level,
        "resolution_notes": incident.resolution_notes,
        "created_at": incident.created_at.isoformat() if incident.created_at else None,
        "updated_at": incident.updated_at.isoformat() if incident.updated_at else None,
    }


@app.post("/incidents", status_code=201)
def create_incident(payload: schemas.IncidentCreate, db: Session = Depends(get_db)) -> dict:
    if not db.get(User, payload.reporter_id):
        raise HTTPException(status_code=404, detail="Reporter not found")

    severity = payload.severity
    if payload.category_id and "severity" not in payload.model_fields_set:
        category = db.get(IncidentCategory, payload.category_id)
        if category:
            severity = category.default_severity

    incident = IncidentReport(
        reporter_id=payload.reporter_id,
        category_id=payload.category_id,
        description=payload.description,
        severity=severity,
        assigned_to=payload.assigned_to,
        escalation_level=payload.escalation_level,
        status="reported",
    )
    db.add(incident)
    db.commit()
    return _incident_dict(incident)


@app.patch("/incidents/{incident_id}")
def update_incident(
    incident_id: int, payload: schemas.IncidentUpdate, db: Session = Depends(get_db)
) -> dict:
    incident = db.get(IncidentReport, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)
    incident.updated_at = datetime.now(timezone.utc)
    db.commit()
    return _incident_dict(incident)


# ---------------------------------------------------------------------------
# 5. Policy Health Dashboard
# ---------------------------------------------------------------------------
@app.post("/feedback", status_code=201)
def create_feedback(payload: schemas.FeedbackCreate, db: Session = Depends(get_db)) -> dict:
    if not db.get(Message, payload.message_id):
        raise HTTPException(status_code=404, detail="Message not found")
    feedback = Feedback(**payload.model_dump())
    db.add(feedback)
    db.commit()
    return {"id": feedback.id, "message_id": feedback.message_id, "rating": feedback.rating}


@app.get("/dashboard/policy-health")
def policy_health(db: Session = Depends(get_db)) -> dict:
    policies_by_status = db.execute(
        text("select status, count(*) as count from policies group by status order by status")
    ).mappings().all()

    reviews_due = db.execute(
        text(
            """
            WITH current_versions AS (
                SELECT DISTINCT ON (pv.policy_id) pv.policy_id, pv.review_date, pv.requires_review
                FROM policy_versions pv
                ORDER BY pv.policy_id, pv.created_at DESC, pv.id DESC
            )
            SELECT count(*) AS count
            FROM current_versions cv
            JOIN policies p ON p.id = cv.policy_id
            WHERE p.status = 'approved'
              AND cv.requires_review = true
              AND cv.review_date IS NOT NULL
              AND cv.review_date <= (current_date + interval '30 days')
            """
        )
    ).scalar()

    clarifications_by_status = db.execute(
        text("select status, count(*) as count from clarification_requests group by status")
    ).mappings().all()

    incidents_by_status = db.execute(
        text("select status, count(*) as count from incident_reports group by status")
    ).mappings().all()

    incidents_by_severity = db.execute(
        text("select severity, count(*) as count from incident_reports group by severity")
    ).mappings().all()

    feedback_totals = db.execute(
        text(
            """
            SELECT count(*) AS total,
                   count(*) FILTER (WHERE rating) AS helpful,
                   count(*) FILTER (WHERE NOT rating) AS not_helpful
            FROM feedback
            """
        )
    ).mappings().one()

    top_cited = db.execute(
        text(
            """
            SELECT p.id, p.title, count(pc.id) AS citation_count
            FROM policy_citations pc
            JOIN policy_versions pv ON pv.id = pc.policy_version_id
            JOIN policies p ON p.id = pv.policy_id
            GROUP BY p.id, p.title
            ORDER BY citation_count DESC, p.title
            LIMIT 5
            """
        )
    ).mappings().all()

    totals = db.execute(
        text(
            """
            SELECT (SELECT count(*) FROM policies) AS policies,
                   (SELECT count(*) FROM conversations) AS conversations,
                   (SELECT count(*) FROM messages) AS messages,
                   (SELECT count(*) FROM incident_reports) AS incidents
            """
        )
    ).mappings().one()

    total_feedback = feedback_totals["total"] or 0
    helpful = feedback_totals["helpful"] or 0

    return {
        "totals": dict(totals),
        "policies_by_status": [dict(r) for r in policies_by_status],
        "reviews_due": reviews_due,
        "clarifications_by_status": [dict(r) for r in clarifications_by_status],
        "incidents_by_status": [dict(r) for r in incidents_by_status],
        "incidents_by_severity": [dict(r) for r in incidents_by_severity],
        "feedback": {
            "total": total_feedback,
            "helpful": helpful,
            "not_helpful": feedback_totals["not_helpful"] or 0,
            "helpful_rate": round(helpful / total_feedback, 3) if total_feedback else None,
        },
        "top_cited_policies": [dict(r) for r in top_cited],
    }
