"""Week 7 clarification messaging: read model, workflow, and authorization.

A "thread" is a ``clarification_requests`` row. The originating employee is
``user_id``; the policy owner is ``assigned_to``; the question is the linked
``messages`` row; replies live in ``clarification_replies``. This module keeps
that model and adds the workflow around it:

    employee asks -> answer -> request clarification -> owner notified
    -> owner replies -> employee replies -> resolve -> reopen

Every endpoint requires a verified bearer token. The actor is never taken from
the request body. Visibility is:

    System Administrator  -> all threads (single-tenant organisation)
    Policy Owner          -> threads assigned to them or they replied to
    Employee              -> threads they requested or replied to

Threads with no policy owner are left unassigned and appear in the admin
triage queue. That is deliberate: guessing an owner is worse than a queue.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

import schemas
from database import get_db
from models import (
    ClarificationRead,
    ClarificationReply,
    ClarificationRequest,
    Conversation,
    Message,
    Policy,
    PolicyCitation,
    PolicyVersion,
)
from security import (
    ADMIN_ROLE,
    POLICY_OWNER_ROLE,
    Identity,
    assert_thread_access,
    get_identity,
    require_admin,
    require_governance,
    visibility_sql,
)

router = APIRouter(tags=["messaging"])

FOLDERS = ("inbox", "requests", "resolved", "triage", "all")
ADMIN_ONLY_FOLDERS = {"triage", "all"}
CLOSED_STATUSES = ("resolved", "closed")

# One projection is reused by the list, detail, notification, and governance
# read models so counts and visibility cannot drift between screens.
THREAD_SELECT = """
SELECT cr.id, cr.conversation_id, cr.message_id, cr.user_id, cr.policy_id,
       cr.reason, cr.status, cr.assigned_to, cr.resolved_at, cr.created_at,
       p.title AS policy_title,
       ru.first_name || ' ' || ru.last_name AS requester_name,
       ru.email AS requester_email,
       rud.name AS requester_department,
       rro.name AS requester_role,
       au.first_name || ' ' || au.last_name AS assignee_name,
       au.email AS assignee_email,
       aud.name AS assignee_department,
       aro.name AS assignee_role,
       qm.body AS question_body,
       (SELECT count(*) FROM clarification_replies r
          WHERE r.request_id = cr.id) AS reply_count,
       (SELECT count(*) FROM clarification_replies r
          WHERE r.request_id = cr.id
            AND r.sender_id <> :uid
            AND r.created_at > COALESCE(rd.last_read_at, to_timestamp(0))) AS unread_count,
       rd.last_read_at,
       lr.body AS last_reply_body,
       lr.created_at AS last_reply_at,
       lr.sender_id AS last_reply_sender,
       (SELECT su.first_name || ' ' || su.last_name FROM users su
          WHERE su.id = lr.sender_id) AS last_reply_sender_name,
       COALESCE(lr.created_at, cr.created_at) AS last_activity
FROM clarification_requests cr
LEFT JOIN policies p ON p.id = cr.policy_id
LEFT JOIN users ru ON ru.id = cr.user_id
LEFT JOIN users au ON au.id = cr.assigned_to
LEFT JOIN departments rud ON rud.id = ru.department_id
LEFT JOIN departments aud ON aud.id = au.department_id
LEFT JOIN roles rro ON rro.id = ru.role_id
LEFT JOIN roles aro ON aro.id = au.role_id
LEFT JOIN messages qm ON qm.id = cr.message_id
LEFT JOIN clarification_reads rd
       ON rd.request_id = cr.id AND rd.user_id = :uid
LEFT JOIN LATERAL (
    SELECT r.body, r.created_at, r.sender_id
    FROM clarification_replies r
    WHERE r.request_id = cr.id
    ORDER BY r.created_at DESC, r.id DESC
    LIMIT 1
) lr ON TRUE
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _iso(value) -> Optional[str]:
    return value.isoformat() if value else None


# The database keeps four workflow states (open, in_progress, resolved,
# closed). The product vocabulary is five: who is holding the thread next.
# Deriving it once on the server keeps the UI and the API in agreement.
ESCALATION_STATUSES = (
    "open",
    "triage",
    "awaiting_owner",
    "awaiting_employee",
    "resolved",
    "closed",
)


def _escalation_status(row) -> str:
    if row["status"] == "closed":
        return "closed"
    if row["status"] == "resolved":
        return "resolved"
    if row["assigned_to"] is None:
        return "triage"
    last_sender = row["last_reply_sender"]
    if last_sender is None or last_sender == row["user_id"]:
        return "awaiting_owner"
    return "awaiting_employee"


def _unread_count(row, identity: Identity) -> int:
    """Replies from someone else since the last read, plus a new assignment."""
    unread = int(row["unread_count"] or 0)
    # A thread assigned to *me* with no reply and no read watermark is new work.
    if (
        row["assigned_to"] == identity.user_id
        and row["last_read_at"] is None
    ):
        unread = max(unread, 1)
    return unread


def _permissions(row, identity: Identity) -> dict:
    me = identity.user_id
    closed = row["status"] in CLOSED_STATUSES
    participant = (
        identity.is_admin
        or row["user_id"] == me
        or row["assigned_to"] == me
    )
    return {
        "can_reply": participant and not closed,
        "can_resolve": participant and not closed,
        "can_reopen": (row["user_id"] == me or identity.is_admin) and closed,
        "can_close": participant and row["status"] == "resolved",
        "can_assign": identity.is_admin,
    }


def _serialize(row, identity: Identity) -> dict:
    return {
        "id": row["id"],
        "subject": row["policy_title"] or "Policy clarification",
        "policy": (
            {"id": row["policy_id"], "title": row["policy_title"]}
            if row["policy_id"]
            else None
        ),
        "requester": {
            "id": row["user_id"],
            "name": row["requester_name"],
            "email": row["requester_email"],
            "role": row["requester_role"],
            "department": row["requester_department"],
        },
        "assignee": (
            {
                "id": row["assigned_to"],
                "name": row["assignee_name"],
                "email": row["assignee_email"],
                "role": row["assignee_role"],
                "department": row["assignee_department"],
            }
            if row["assigned_to"]
            else None
        ),
        "status": row["status"],
        "escalation_status": _escalation_status(row),
        "is_triage": row["assigned_to"] is None,
        "question": row["question_body"] or row["reason"] or "",
        "reason": row["reason"],
        "created_at": _iso(row["created_at"]),
        "updated_at": _iso(row["last_activity"]),
        "resolved_at": _iso(row["resolved_at"]),
        "reply_count": int(row["reply_count"] or 0),
        "unread_count": _unread_count(row, identity),
        "last_reply": (
            {
                "body": row["last_reply_body"],
                "sender_id": row["last_reply_sender"],
                "created_at": _iso(row["last_reply_at"]),
            }
            if row["last_reply_at"]
            else None
        ),
        "permissions": _permissions(row, identity),
    }


def _folder_predicate(folder: str) -> str:
    if folder == "inbox":
        return (
            "(cr.assigned_to = :uid OR EXISTS (SELECT 1 FROM clarification_replies ir "
            "WHERE ir.request_id = cr.id AND ir.sender_id <> :uid))"
        )
    if folder == "requests":
        return "cr.user_id = :uid"
    if folder == "resolved":
        return "cr.status IN ('resolved', 'closed')"
    if folder == "triage":
        return "cr.assigned_to IS NULL"
    return "TRUE"


def _validate_folder(folder: str, identity: Identity) -> None:
    if folder not in FOLDERS:
        raise HTTPException(status_code=422, detail="Unknown folder")
    if folder in ADMIN_ONLY_FOLDERS and not identity.is_admin:
        raise HTTPException(status_code=403, detail="Administrator access required")


LAST_REPLY_SENDER = (
    "(SELECT lrs.sender_id FROM clarification_replies lrs "
    "WHERE lrs.request_id = cr.id ORDER BY lrs.created_at DESC, lrs.id DESC LIMIT 1)"
)


def _status_predicate(status: Optional[str]) -> str:
    """SQL for the derived escalation vocabulary; also used by folder counts."""
    if not status:
        return "TRUE"
    if status == "open":
        return "cr.status = 'open'"
    if status == "triage":
        return "cr.assigned_to IS NULL AND cr.status IN ('open', 'in_progress')"
    if status == "awaiting_owner":
        return (
            "cr.status IN ('open', 'in_progress') AND cr.assigned_to IS NOT NULL "
            f"AND COALESCE({LAST_REPLY_SENDER}, cr.user_id) = cr.user_id"
        )
    if status == "awaiting_employee":
        return (
            "cr.status IN ('open', 'in_progress') AND cr.assigned_to IS NOT NULL "
            f"AND {LAST_REPLY_SENDER} IS NOT NULL AND {LAST_REPLY_SENDER} <> cr.user_id"
        )
    if status in ("resolved", "closed"):
        return f"cr.status = '{status}'"
    raise HTTPException(status_code=422, detail="Unknown escalation status")


def _base_params(identity: Identity, include_search: bool = False, q: Optional[str] = None) -> dict:
    params = {"uid": identity.user_id}
    clause, scope_params = visibility_sql(identity, "cr")
    params.update(scope_params)
    params["scope"] = clause
    if include_search:
        params["q"] = q or ""
        params["like"] = f"%{(q or '').strip()}%"
    return params


def _search_predicate() -> str:
    return (
        "(:q = '' OR p.title ILIKE :like OR cr.reason ILIKE :like "
        "OR qm.body ILIKE :like OR EXISTS (SELECT 1 FROM clarification_replies sr "
        "WHERE sr.request_id = cr.id AND sr.body ILIKE :like))"
    )


def _thread_count(
    db: Session, identity: Identity, folder: str, q: Optional[str] = None, status: Optional[str] = None
) -> tuple:
    params = _base_params(identity, include_search=True, q=q)
    row = db.execute(
        text(
            f"""
            SELECT count(*) AS total,
                   COALESCE(sum((
                       SELECT count(*) FROM clarification_replies r
                       WHERE r.request_id = cr.id AND r.sender_id <> :uid
                         AND r.created_at > COALESCE(rd.last_read_at, to_timestamp(0))
                   )), 0)::int AS reply_unread,
                   count(*) FILTER (
                       WHERE cr.assigned_to = :uid AND rd.last_read_at IS NULL
                         AND NOT EXISTS (SELECT 1 FROM clarification_replies r2
                                         WHERE r2.request_id = cr.id AND r2.sender_id <> :uid)
                   )::int AS new_assignments
            FROM clarification_requests cr
            LEFT JOIN policies p ON p.id = cr.policy_id
            LEFT JOIN messages qm ON qm.id = cr.message_id
            LEFT JOIN clarification_reads rd
                   ON rd.request_id = cr.id AND rd.user_id = :uid
            WHERE ({params['scope']}) AND {_folder_predicate(folder)}
              AND {_status_predicate(status)}
              AND {_search_predicate()}
            """
        ),
        params,
    ).mappings().one()
    total = int(row["total"] or 0)
    unread = int(row["reply_unread"] or 0) + int(row["new_assignments"] or 0)
    return total, unread


def _load_row(db: Session, identity: Identity, request_id: int):
    params = _base_params(identity)
    params["rid"] = request_id
    return db.execute(
        text(
            f"{THREAD_SELECT} WHERE cr.id = :rid AND ({params['scope']})"
        ),
        params,
    ).mappings().first()


def _tenant_has_owner(db: Session, policy_id: Optional[int]) -> Optional[int]:
    if not policy_id:
        return None
    return db.execute(
        text("SELECT owner_id FROM policies WHERE id = :pid"), {"pid": policy_id}
    ).scalar()


def _mark_read(db: Session, request_id: int, user_id: int) -> None:
    """Upsert a read watermark without ever touching anyone else's row."""
    db.execute(
        text(
            """
            INSERT INTO clarification_reads (request_id, user_id, last_read_at)
            VALUES (:rid, :uid, now())
            ON CONFLICT (request_id, user_id)
            DO UPDATE SET last_read_at = EXCLUDED.last_read_at
            """
        ),
        {"rid": request_id, "uid": user_id},
    )


def _conversation_answer(db: Session, conversation_id: Optional[int]) -> dict:
    """Return the originating answer and its citations for thread detail."""
    if not conversation_id:
        return {"answer": None, "citations": []}
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        return {"answer": None, "citations": []}
    answer_message = None
    for message in conversation.messages:
        if message.sender == "derexi":
            answer_message = message
            break
    if not answer_message:
        return {"answer": None, "citations": []}
    citations = []
    for citation in answer_message.citations:
        version = db.get(PolicyVersion, citation.policy_version_id)
        citations.append(
            {
                "policy_id": version.policy_id if version else None,
                "policy_version_id": citation.policy_version_id,
                "title": version.title if version else None,
                "version_no": version.version_no if version else None,
                "excerpt": citation.excerpt,
            }
        )
    return {"answer": answer_message.body, "citations": citations}


def _thread_detail(db: Session, identity: Identity, request_id: int) -> dict:
    row = _load_row(db, identity, request_id)
    if not row:
        raise HTTPException(status_code=404, detail="Clarification request not found")
    data = _serialize(row, identity)
    answer = _conversation_answer(db, row["conversation_id"])
    data["answer"] = answer["answer"]
    data["citations"] = answer["citations"]
    replies = db.execute(
        text(
            """
            SELECT r.id, r.sender_id, r.body, r.created_at,
                   u.first_name || ' ' || u.last_name AS sender_name,
                   u.role_id,
                   ro.name AS sender_role
            FROM clarification_replies r
            JOIN users u ON u.id = r.sender_id
            JOIN roles ro ON ro.id = u.role_id
            WHERE r.request_id = :rid
            ORDER BY r.created_at, r.id
            """
        ),
        {"rid": request_id},
    ).mappings().all()
    data["replies"] = [
        {
            "id": reply["id"],
            "sender_id": reply["sender_id"],
            "sender": reply["sender_name"],
            "sender_role": reply["sender_role"],
            "body": reply["body"],
            "created_at": _iso(reply["created_at"]),
            "mine": reply["sender_id"] == identity.user_id,
        }
        for reply in replies
    ]
    data["participants"] = _participants(db, row, replies)
    return data


def _participants(db: Session, row, replies) -> list:
    out = []
    seen = set()

    def add(user_id, name, role):
        if not user_id or user_id in seen:
            return
        seen.add(user_id)
        out.append({"id": user_id, "name": name, "role": role})

    add(row["user_id"], row["requester_name"], row["requester_role"])
    add(row["assigned_to"], row["assignee_name"], row["assignee_role"])
    for reply in replies:
        if reply["sender_id"] not in seen:
            add(reply["sender_id"], reply["sender_name"], reply["sender_role"])
    return out


# ---------------------------------------------------------------------------
# Read model
# ---------------------------------------------------------------------------
@router.get("/messages")
def list_messages(
    folder: str = Query(default="inbox"),
    q: Optional[str] = Query(default=None, max_length=100),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    identity: Identity = Depends(get_identity),
    db: Session = Depends(get_db),
) -> dict:
    """Scoped, searchable thread list plus folder counts and unread totals."""
    _validate_folder(folder, identity)
    status_clause = _status_predicate(status)
    params = _base_params(identity, include_search=True, q=q)
    params.update({"limit": limit, "offset": offset})
    rows = db.execute(
        text(
            f"""
            {THREAD_SELECT}
            WHERE ({params['scope']}) AND {_folder_predicate(folder)}
              AND {status_clause}
              AND {_search_predicate()}
            ORDER BY last_activity DESC, cr.id DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        params,
    ).mappings().all()

    folders = []
    for name in FOLDERS:
        if name in ADMIN_ONLY_FOLDERS and not identity.is_admin:
            continue
        # Folder badges describe the folder, not the current search result.
        total, unread = _thread_count(db, identity, name)
        folders.append(
            {
                "id": name,
                "label": {
                    "inbox": "Inbox",
                    "requests": "My requests",
                    "resolved": "Resolved",
                    "triage": "Triage queue",
                    "all": "All threads",
                }[name],
                "count": total,
                "unread": unread,
            }
        )

    # Count the visible set once: folders overlap, and previews are paginated.
    _, unread_total = _thread_count(db, identity, "all")

    return {
        "folder": folder,
        "query": q or "",
        "status": status or "",
        "escalation_statuses": list(ESCALATION_STATUSES),
        "threads": [_serialize(row, identity) for row in rows],
        "folders": folders,
        "unread_total": unread_total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/messages/notifications")
def list_notifications(
    identity: Identity = Depends(get_identity),
    db: Session = Depends(get_db),
) -> dict:
    """In-app notifications derived from unread threads (no separate queue)."""
    params = _base_params(identity)
    rows = db.execute(
        text(
            f"""
            {THREAD_SELECT}
            WHERE ({params['scope']}) AND (
                EXISTS (SELECT 1 FROM clarification_replies nr
                        WHERE nr.request_id = cr.id AND nr.sender_id <> :uid
                          AND nr.created_at > COALESCE(rd.last_read_at, to_timestamp(0)))
                OR (cr.assigned_to = :uid AND rd.last_read_at IS NULL)
            )
            ORDER BY last_activity DESC, cr.id DESC
            LIMIT 100
            """
        ),
        params,
    ).mappings().all()

    items = []
    _, unread_total = _thread_count(db, identity, "all")
    for row in rows:
        unread = _unread_count(row, identity)
        if unread <= 0:
            continue
        if row["assigned_to"] is None and identity.is_admin:
            kind = "triage"
            actor = row["requester_name"]
        elif row["assigned_to"] == identity.user_id and int(row["reply_count"] or 0) == 0:
            kind = "assigned"
            actor = row["requester_name"]
        else:
            kind = "reply"
            actor = row["last_reply_sender_name"] or row["assignee_name"] or row["requester_name"]
        items.append(
            {
                "thread_id": row["id"],
                "kind": kind,
                "subject": row["policy_title"] or "Policy clarification",
                "actor": actor,
                "snippet": row["last_reply_body"] or row["question_body"] or row["reason"] or "",
                "at": _iso(row["last_activity"]),
                "unread": unread,
            }
        )
        if len(items) >= 20:
            break

    triage = 0
    if identity.is_admin:
        triage = db.execute(
            text("SELECT count(*) FROM clarification_requests WHERE assigned_to IS NULL")
        ).scalar() or 0

    return {"unread_total": unread_total, "items": items, "triage_count": int(triage)}


# ---------------------------------------------------------------------------
# Governance list (kept for the existing Governance > Clarifications tab)
# ---------------------------------------------------------------------------
@router.get("/clarifications")
def list_clarifications(
    status: Optional[str] = Query(default=None, pattern="^(open|in_progress|resolved|closed)$"),
    assigned_to: Optional[int] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    identity: Identity = Depends(require_governance),
    db: Session = Depends(get_db),
) -> list:
    if assigned_to is not None and not identity.is_admin and assigned_to != identity.user_id:
        raise HTTPException(status_code=403, detail="You can only list your own assignments")

    params = _base_params(identity)
    conditions = [f"({params['scope']})"]
    if status:
        conditions.append("cr.status = :status")
        params["status"] = status
    if assigned_to is not None:
        conditions.append("cr.assigned_to = :assigned_to")
        params["assigned_to"] = assigned_to
    params["limit"] = limit

    rows = db.execute(
        text(
            f"""
            {THREAD_SELECT}
            WHERE {' AND '.join(conditions)}
            ORDER BY last_activity DESC, cr.id DESC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()

    out = []
    for row in rows:
        item = _serialize(row, identity)
        item.update(
            {
                "user_id": row["user_id"],
                "requester": row["requester_name"],
                "policy_id": row["policy_id"],
                "policy_title": row["policy_title"],
                "assigned_to": row["assigned_to"],
                "assignee": row["assignee_name"],
                "reason": row["reason"],
            }
        )
        out.append(item)
    return out


# ---------------------------------------------------------------------------
# Create a clarification from a Policy Assistant answer
# ---------------------------------------------------------------------------
@router.post("/clarifications", status_code=201)
def create_clarification(
    payload: schemas.ClarificationCreate,
    identity: Identity = Depends(get_identity),
    db: Session = Depends(get_db),
) -> dict:
    if payload.user_id is not None and payload.user_id != identity.user_id:
        raise HTTPException(status_code=403, detail="Identity mismatch")

    conversation_id = payload.conversation_id
    if payload.message_id is not None:
        message = db.get(Message, payload.message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        if conversation_id is not None and message.conversation_id != conversation_id:
            raise HTTPException(status_code=422, detail="Message does not belong to that conversation")
        conversation_id = message.conversation_id

    if conversation_id is None:
        raise HTTPException(status_code=422, detail="conversation_id is required")

    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != identity.user_id:
        # 404 prevents probing another employee's conversation ids.
        raise HTTPException(status_code=404, detail="Conversation not found")

    question = None
    if payload.message_id is not None:
        question = db.get(Message, payload.message_id)
        if question.sender != "user":
            raise HTTPException(status_code=422, detail="Clarification must reference the employee's question")
    else:
        question = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id, Message.sender == "user")
            .order_by(Message.id)
            .first()
        )

    context = payload.context or payload.reason
    if not context or len(context.strip()) < 2:
        raise HTTPException(status_code=422, detail="Clarification context is required")

    policy_id = payload.policy_id
    if policy_id is not None:
        cited = db.execute(
            text(
                """
                SELECT 1
                FROM policy_citations pc
                JOIN policy_versions pv ON pv.id = pc.policy_version_id
                JOIN messages m ON m.id = pc.message_id
                WHERE m.conversation_id = :cid AND pv.policy_id = :pid
                LIMIT 1
                """
            ),
            {"cid": conversation_id, "pid": policy_id},
        ).first()
        if not cited:
            raise HTTPException(
                status_code=422,
                detail="That policy is not part of this answer; choose a cited policy",
            )
    else:
        policy_id = db.execute(
            text(
                """
                SELECT pv.policy_id
                FROM policy_citations pc
                JOIN policy_versions pv ON pv.id = pc.policy_version_id
                JOIN messages m ON m.id = pc.message_id
                WHERE m.conversation_id = :cid
                ORDER BY m.id, pc.id
                LIMIT 1
                """
            ),
            {"cid": conversation_id},
        ).scalar()

    if not db.get(Policy, policy_id):
        policy_id = None

    duplicate = db.execute(
        text(
            """
            SELECT id FROM clarification_requests
            WHERE conversation_id = :cid
              AND status IN ('open', 'in_progress')
              AND policy_id IS NOT DISTINCT FROM :pid
            ORDER BY id DESC LIMIT 1
            """
        ),
        {"cid": conversation_id, "pid": policy_id},
    ).scalar()
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail=f"A clarification thread already exists for this answer (#{duplicate})",
        )

    # Never guess an owner. No owner means the admin triage queue.
    assigned_to = _tenant_has_owner(db, policy_id)

    request = ClarificationRequest(
        conversation_id=conversation_id,
        message_id=question.id if question else None,
        user_id=identity.user_id,
        policy_id=policy_id,
        reason=context.strip(),
        status="open",
        assigned_to=assigned_to,
    )
    db.add(request)
    db.flush()
    _mark_read(db, request.id, identity.user_id)
    conversation.updated_at = datetime.now(timezone.utc)
    db.commit()

    return _thread_detail(db, identity, request.id)


# ---------------------------------------------------------------------------
# Thread detail and workflow
# ---------------------------------------------------------------------------
@router.get("/clarifications/{request_id}")
def get_clarification(
    request_id: int,
    identity: Identity = Depends(get_identity),
    db: Session = Depends(get_db),
) -> dict:
    return _thread_detail(db, identity, request_id)


@router.post("/clarifications/{request_id}/replies", status_code=201)
def add_clarification_reply(
    request_id: int,
    payload: schemas.ClarificationReplyCreate,
    identity: Identity = Depends(get_identity),
    db: Session = Depends(get_db),
) -> dict:
    if payload.sender_id is not None and payload.sender_id != identity.user_id:
        raise HTTPException(status_code=403, detail="Identity mismatch")
    assert_thread_access(db, identity, request_id)

    request = db.get(ClarificationRequest, request_id)
    if not (identity.is_admin or request.user_id == identity.user_id
            or request.assigned_to == identity.user_id):
        raise HTTPException(status_code=403, detail="Only the requester, current assignee, or an administrator can reply")
    if request.status in CLOSED_STATUSES:
        raise HTTPException(status_code=409, detail="Thread is resolved; reopen it before replying")

    reply = ClarificationReply(
        request_id=request_id,
        sender_id=identity.user_id,
        body=payload.body.strip(),
    )
    db.add(reply)
    if request.status == "open":
        request.status = "in_progress"
    if request.conversation_id:
        conversation = db.get(Conversation, request.conversation_id)
        if conversation:
            conversation.updated_at = datetime.now(timezone.utc)
    _mark_read(db, request_id, identity.user_id)
    db.commit()

    return {
        "id": reply.id,
        "request_id": request_id,
        "sender_id": identity.user_id,
        "body": reply.body,
        "created_at": _iso(reply.created_at),
        "status": request.status,
    }


@router.post("/clarifications/{request_id}/resolve")
def resolve_clarification(
    request_id: int,
    identity: Identity = Depends(get_identity),
    db: Session = Depends(get_db),
) -> dict:
    assert_thread_access(db, identity, request_id)
    request = db.get(ClarificationRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Clarification request not found")

    allowed = (
        identity.is_admin
        or request.user_id == identity.user_id
        or request.assigned_to == identity.user_id
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="Only the requester, assignee, or an administrator can resolve")

    if request.status not in CLOSED_STATUSES:
        request.status = "resolved"
        request.resolved_at = datetime.now(timezone.utc)
        _mark_read(db, request_id, identity.user_id)
        db.commit()
    return {"id": request.id, "status": request.status, "resolved_at": _iso(request.resolved_at)}


@router.post("/clarifications/{request_id}/close")
def close_clarification(
    request_id: int,
    identity: Identity = Depends(get_identity),
    db: Session = Depends(get_db),
) -> dict:
    """Resolved threads may be archived as closed; only participants or admins."""
    assert_thread_access(db, identity, request_id)
    request = db.get(ClarificationRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Clarification request not found")
    allowed = (
        identity.is_admin
        or request.user_id == identity.user_id
        or request.assigned_to == identity.user_id
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="Only a participant can close this thread")
    if request.status == "closed":
        return {"id": request.id, "status": "closed", "resolved_at": _iso(request.resolved_at)}
    if request.status != "resolved":
        raise HTTPException(status_code=409, detail="Resolve the thread before closing it")

    request.status = "closed"
    db.commit()
    return {"id": request.id, "status": request.status, "resolved_at": _iso(request.resolved_at)}


@router.post("/clarifications/{request_id}/reopen")
def reopen_clarification(
    request_id: int,
    payload: Optional[schemas.ClarificationReopen] = None,
    identity: Identity = Depends(get_identity),
    db: Session = Depends(get_db),
) -> dict:
    assert_thread_access(db, identity, request_id)
    request = db.get(ClarificationRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Clarification request not found")
    if not (identity.is_admin or request.user_id == identity.user_id):
        raise HTTPException(status_code=403, detail="Only the requester or an administrator can reopen")
    if request.status not in CLOSED_STATUSES:
        raise HTTPException(status_code=409, detail="Thread is already open")

    request.status = "open"
    request.resolved_at = None
    reason = (payload.reason if payload else None) or "Thread reopened."
    db.add(
        ClarificationReply(
            request_id=request_id,
            sender_id=identity.user_id,
            body=reason.strip(),
        )
    )
    _mark_read(db, request_id, identity.user_id)
    db.commit()
    return {"id": request.id, "status": request.status, "resolved_at": None}


@router.post("/clarifications/{request_id}/read")
def mark_clarification_read(
    request_id: int,
    identity: Identity = Depends(get_identity),
    db: Session = Depends(get_db),
) -> dict:
    assert_thread_access(db, identity, request_id)
    _mark_read(db, request_id, identity.user_id)
    db.commit()
    return {"id": request_id, "unread_count": 0}


@router.post("/clarifications/{request_id}/assign")
def assign_clarification(
    request_id: int,
    payload: schemas.ClarificationAssign,
    identity: Identity = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    request = db.get(ClarificationRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Clarification request not found")
    target = db.execute(
        text(
            """
            SELECT u.id, r.name AS role
            FROM users u JOIN roles r ON r.id = u.role_id
            WHERE u.id = :uid
            """
        ),
        {"uid": payload.assignee_id},
    ).mappings().first()
    if not target:
        raise HTTPException(status_code=404, detail="Assignee not found")
    if target["role"] not in (POLICY_OWNER_ROLE, ADMIN_ROLE):
        raise HTTPException(status_code=422, detail="Assignee must be a policy owner or administrator")

    if request.assigned_to != target["id"]:
        # A fresh assignment is unread even if this person handled it earlier.
        db.execute(text("DELETE FROM clarification_reads WHERE request_id = :rid AND user_id = :uid"),
                   {"rid": request_id, "uid": target["id"]})
        request.assigned_to = target["id"]
    db.commit()
    return _thread_detail(db, identity, request_id)
