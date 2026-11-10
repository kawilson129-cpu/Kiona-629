"""Transactional Week 8 policy lifecycle. No schema creation or background writes."""
import json
import logging
from urllib.parse import unquote
from datetime import date, datetime, timezone
from typing import Literal, Optional
from urllib.parse import urlsplit
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.exc import IntegrityError, ProgrammingError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from database import get_db
from models import (GovernanceDraft as Draft, GovernanceEvent as Event, User, Role,
                    Policy, PolicyVersion, PolicyCategory, Department, ClarificationRequest)
from security import Identity, require_governance, POLICY_OWNER_ROLE

import document_intake as intake
log = logging.getLogger(__name__)
router = APIRouter(prefix='/governance', tags=['governance'])


def workflow_db(db: Session = Depends(get_db)):
    try:
        yield db
    except (IntegrityError, StaleDataError):
        db.rollback()
        raise HTTPException(status_code=409, detail='Concurrent change or policy/version conflict; refresh before retrying')
    except ProgrammingError as exc:
        db.rollback()
        if getattr(exc.orig, 'pgcode', None) in ('42P01', '42703'):
            log.warning('Governance schema dependency missing: SQLSTATE %s', getattr(exc.orig, 'pgcode', None))
            raise HTTPException(status_code=503, detail='Policy workspace is temporarily unavailable. Please try again later.')
        raise


class Source(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    url: str = Field(max_length=2048)
    title: str = Field(min_length=1, max_length=500)
    published: Optional[date] = None
    context: str = Field(min_length=1, max_length=4000)
    @model_validator(mode='after')
    def safe_url(self):
        u = urlsplit(self.url)
        if u.scheme != 'https' or not u.hostname or u.username or u.password:
            raise ValueError('Source must be an HTTPS publication URL')
        return self

class Content(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    summary: Optional[str] = Field(default=None, max_length=1000)
    body: str = Field(min_length=1, max_length=20000)
    version_no: str = Field(min_length=1, max_length=20)
    category_id: Optional[int] = None
    effective_date: Optional[date] = None
    review_date: Optional[date] = None
    source: Optional[Source] = None

class Create(Content):
    import_id: Optional[str] = Field(default=None, max_length=100)
    confirm_document: bool = False
    policy_id: Optional[int] = None
    department_id: Optional[int] = None

class Edit(Content):
    expected_revision: int

class Action(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    expected_revision: int
    action: Literal['submit', 'peer_approve', 'peer_reject', 'peer_changes',
                    'final_approve', 'final_reject', 'final_changes', 'publish']
    reviewer_id: Optional[int] = None
    comment: Optional[str] = Field(default=None, max_length=4000)


def fail(code, detail):
    raise HTTPException(status_code=code, detail=detail)


def draft(db, did, actor, lock=False):
    q = db.query(Draft).filter(Draft.id == did)
    if lock:
        q = q.with_for_update()
    d = q.first()
    if not d:
        fail(404, 'Draft not found')
    if not actor.is_admin and actor.department_id != d.department_id:
        fail(403, 'Department access required')
    return d


def reviewer_valid(db, uid, d):
    user = db.get(User, uid) if uid else None
    return bool(user and user.id != d.author_id and user.department_id == d.department_id
                and user.role and user.role.name == POLICY_OWNER_ROLE)


def serialize(d):
    values = {k: getattr(d, k) for k in ('id','policy_id','base_version_id','department_id',
        'author_id','reviewer_id','title','summary','body','version_no','category_id','status',
        'revision','peer_approved_by','final_approved_by','published_version_id')}
    for k in ('effective_date','review_date','created_at','updated_at'):
        value = getattr(d,k)
        values[k] = value.isoformat() if value else None
    values['source'] = json.loads(d.source_json) if d.source_json else None
    return values


def record(db, d, actor, action, comment=None, document=None):
    d.updated_at = datetime.now(timezone.utc)
    db.flush()
    snapshot = serialize(d)
    if document: snapshot['original_document'] = document
    db.add(Event(draft_id=d.id, actor_id=actor.user_id, action=action, comment=comment,
                 snapshot_json=json.dumps(snapshot)))


def notify(db, d, actor, recipients, message):
    # Reuse Week 7's assignment/read-watermark infrastructure, bell and inbox.
    # Replies to these notices never change the policy workflow.
    for uid in set(recipients) - {actor.user_id}:
        db.add(ClarificationRequest(user_id=actor.user_id, assigned_to=uid,
            policy_id=d.policy_id, status='open',
            reason=f'[Governance #{d.id}] {d.title}: {message} /ui/#governance/{d.id}'))


def admins(db):
    return [u.id for u in db.query(User).join(Role).filter(Role.name == 'System Administrator')]


def save(db):
    try:
        db.commit()
    except (IntegrityError, StaleDataError):
        db.rollback()
        fail(409, 'Concurrent change or conflicting policy/version; refresh before retrying')


def apply_content(db, d, payload):
    if payload.category_id and not db.get(PolicyCategory, payload.category_id):
        fail(422, 'Unknown category')
    for k in ('title','summary','body','version_no','category_id','effective_date','review_date'):
        setattr(d, k, getattr(payload, k))
    d.source_json = payload.source.model_dump_json() if payload.source else None


@router.get('/drafts')
def drafts(actor: Identity = Depends(require_governance), db: Session = Depends(workflow_db)):
    q = db.query(Draft)
    if not actor.is_admin:
        q = q.filter(Draft.department_id == actor.department_id)
    return [serialize(d) for d in q.order_by(Draft.updated_at.desc(), Draft.id.desc()).all()]


@router.get('/owners')
def owners(actor: Identity = Depends(require_governance), db: Session = Depends(workflow_db)):
    q = db.query(User).join(Role).filter(Role.name == POLICY_OWNER_ROLE)
    if not actor.is_admin:
        q = q.filter(User.department_id == actor.department_id)
    return [{'id':u.id,'name':u.full_name,'department_id':u.department_id} for u in q.order_by(User.id)]


@router.post('/drafts', status_code=201)
def create(payload: Create, actor: Identity = Depends(require_governance), db: Session = Depends(workflow_db)):
    dept = payload.department_id if actor.is_admin else actor.department_id
    if not actor.is_admin and payload.department_id not in (None, dept):
        fail(403, 'Cannot author for another department')
    if not dept or not db.get(Department, dept):
        fail(422, 'Valid department required')
    base = None
    if payload.policy_id:
        p = db.get(Policy, payload.policy_id)
        if not p or p.status != 'approved':
            fail(404, 'Published policy not found')
        owner = db.get(User,p.owner_id) if p.owner_id else None
        if not owner or owner.department_id != dept:
            fail(403, 'Revision must belong to the policy department')
        base = db.query(PolicyVersion).filter(PolicyVersion.policy_id == p.id).order_by(
            PolicyVersion.created_at.desc(),PolicyVersion.id.desc()).first()
    d = Draft(policy_id=payload.policy_id, base_version_id=base.id if base else None,
              author_id=actor.user_id, department_id=dept, status='draft')
    apply_content(db,d,payload)
    db.add(d)
    attachment = None
    claimed = False
    try:
        if payload.import_id:
            item = intake.claim(payload.import_id, actor.user_id, payload.confirm_document)
            claimed = True
            attachment = intake.retain(item)
        record(db,d,actor,'created',document=attachment)
        save(db)
    except Exception:
        db.rollback()
        if claimed: intake.release(payload.import_id, attachment)
        raise
    if claimed: intake.release(payload.import_id, success=True)
    return serialize(d)


@router.get('/drafts/{did}')
def detail(did: int, actor: Identity = Depends(require_governance), db: Session = Depends(workflow_db)):
    d = draft(db,did,actor)
    result = serialize(d)
    base = db.get(PolicyVersion,d.base_version_id) if d.base_version_id else None
    result['base_version'] = {'title':base.title,'body':base.body,'version_no':base.version_no} if base else None
    result['history'] = [{'id':e.id,'actor_id':e.actor_id,'actor': db.get(User,e.actor_id).full_name,
        'action':e.action,'comment':e.comment,'at':e.created_at.isoformat(),
        'snapshot':json.loads(e.snapshot_json)} for e in db.query(Event).filter(
            Event.draft_id == did).order_by(Event.id)]
    return result


@router.patch('/drafts/{did}')
def edit(did: int, payload: Edit, actor: Identity = Depends(require_governance), db: Session = Depends(workflow_db)):
    d = draft(db,did,actor,True)
    if actor.user_id != d.author_id:
        fail(403, 'Only the author can edit a working copy')
    if d.status == 'published':
        fail(409, 'Published content is immutable; propose a new version')
    if payload.expected_revision != d.revision:
        fail(409, 'Draft changed; refresh before editing')
    apply_content(db,d,payload)
    d.status = 'draft'
    d.peer_approved_by = d.final_approved_by = None
    d.reviewer_id = None
    record(db,d,actor,'edited_approvals_invalidated')
    save(db)
    return serialize(d)


@router.post('/drafts/{did}/actions')
def action(did: int, payload: Action, request: Request, actor: Identity = Depends(require_governance), db: Session = Depends(workflow_db)):
    request.state.security_action = payload.action
    d = draft(db,did,actor,True)
    if payload.expected_revision != d.revision:
        fail(409, 'Draft changed; refresh before reviewing')
    a = payload.action
    if a == 'submit':
        if actor.user_id != d.author_id:
            fail(403, 'Only the author can submit')
        if d.status not in ('draft','revisions_requested','rejected'):
            fail(409, 'Draft is already in review')
        if not reviewer_valid(db,payload.reviewer_id,d):
            fail(403, 'Choose another Policy Owner in the same department')
        d.reviewer_id = payload.reviewer_id
        d.peer_approved_by = d.final_approved_by = None
        d.status = 'pending_peer_review'
        notify(db,d,actor,[d.reviewer_id],'Peer review assigned')
    elif a.startswith('peer_'):
        if actor.user_id != d.reviewer_id or not reviewer_valid(db,actor.user_id,d):
            fail(403, 'Assigned independent department Policy Owner required')
        if d.status != 'pending_peer_review':
            fail(409, 'Not awaiting peer review')
        if a == 'peer_approve':
            recipients = [uid for uid in admins(db) if uid != d.author_id]
            if not recipients:
                fail(409, 'An independent System Administrator is required')
            d.peer_approved_by = actor.user_id
            d.status = 'pending_final_approval'
            notify(db,d,actor,recipients,'Final approval requested')
        else:
            if not payload.comment:
                fail(422, 'A review comment is required')
            d.peer_approved_by = d.final_approved_by = None
            d.status = 'rejected' if a == 'peer_reject' else 'revisions_requested'
            notify(db,d,actor,[d.author_id],d.status + ': ' + payload.comment)
    elif a.startswith('final_'):
        if not actor.is_admin or actor.user_id in (d.author_id,d.reviewer_id):
            fail(403, 'Independent System Administrator required')
        if d.status != 'pending_final_approval' or not d.peer_approved_by:
            fail(409, 'Peer approval required')
        if not reviewer_valid(db,d.peer_approved_by,d):
            fail(409, 'Peer role/department changed; author must renew review')
        if a == 'final_approve':
            d.final_approved_by = actor.user_id
            d.status = 'approved_pending_publication'
        else:
            if not payload.comment:
                fail(422, 'A review comment is required')
            d.peer_approved_by = d.final_approved_by = None
            d.status = 'rejected' if a == 'final_reject' else 'revisions_requested'
        notify(db,d,actor,[d.author_id,d.reviewer_id],d.status + (': '+payload.comment if payload.comment else ''))
    elif a == 'publish':
        if not actor.is_admin or actor.user_id == d.author_id:
            fail(403, 'Independent System Administrator required')
        if d.status != 'approved_pending_publication' or not d.peer_approved_by or not d.final_approved_by:
            fail(409, 'Peer and final approvals required')
        approver = db.get(User,d.final_approved_by)
        if not reviewer_valid(db,d.peer_approved_by,d) or not approver or approver.role.name != 'System Administrator':
            fail(409, 'Approver role changed; renew review')
        if d.effective_date and d.effective_date > date.today():
            fail(409, 'Approved; publish on or after the effective date')
        # Serialize simultaneous revisions of the same published policy.
        p = db.query(Policy).filter(Policy.id == d.policy_id).with_for_update().first() if d.policy_id else None
        if p:
            current = db.query(PolicyVersion).filter(PolicyVersion.policy_id == p.id).order_by(
                PolicyVersion.created_at.desc(),PolicyVersion.id.desc()).first()
            if (current.id if current else None) != d.base_version_id:
                fail(409, 'Published base changed; create a fresh revision')
        else:
            owner = db.get(User,d.author_id)
            if not owner.role or owner.role.name != POLICY_OWNER_ROLE or owner.department_id != d.department_id:
                owner = db.get(User,d.reviewer_id)
            p = Policy(title=d.title,summary=d.summary,category_id=d.category_id,owner_id=owner.id,status='approved')
            db.add(p)
            db.flush()
            d.policy_id = p.id
        if db.query(PolicyVersion).filter(PolicyVersion.policy_id==p.id,PolicyVersion.version_no==d.version_no).first():
            fail(409, 'Version number already published')
        p.title,p.summary,p.category_id = d.title,d.summary,d.category_id
        p.updated_at = datetime.now(timezone.utc)
        v = PolicyVersion(policy_id=p.id,version_no=d.version_no,title=d.title,body=d.body,
            effective_date=d.effective_date,review_date=d.review_date,requires_review=True,created_by=d.author_id)
        db.add(v)
        db.flush()
        d.published_version_id = v.id
        d.status = 'published'
        notify(db,d,actor,[d.author_id,d.reviewer_id],'Published version '+d.version_no)
    record(db,d,actor,a,payload.comment)
    save(db)
    return serialize(d)


@router.get('/availability')
def availability(actor: Identity = Depends(require_governance), db: Session = Depends(get_db)):
    ready = True
    try:
        db.query(Draft).limit(0).all()
        db.query(Event).limit(0).all()
    except SQLAlchemyError as exc:
        db.rollback()
        log.warning('Governance availability probe failed (%s)', type(exc).__name__)
        ready = False
    return {**intake.capabilities(), 'queues_available': ready, 'save_available': ready,
            'message': None if ready else 'Policy workspace is temporarily unavailable. You can prepare a document and return later to save it.',
            'templates': intake.TEMPLATES}


@router.post('/documents/preview')
async def preview_document(request: Request, actor: Identity = Depends(require_governance)):
    length = request.headers.get('content-length')
    if length and (not length.isdigit() or int(length) > intake.MAX_BYTES):
        raise HTTPException(413, 'Choose a document smaller than 5 MB.')
    chunks = bytearray()
    async for chunk in request.stream():
        chunks.extend(chunk)
        if len(chunks) > intake.MAX_BYTES:
            raise HTTPException(413, 'Choose a document smaller than 5 MB.')
    return await run_in_threadpool(intake.preview, bytes(chunks),
        unquote(request.headers.get('x-file-name', '')), request.headers.get('content-type', '').split(';')[0], actor.user_id)


@router.delete('/documents/preview/{token}', status_code=200)
def discard_document(token: str, actor: Identity = Depends(require_governance)):
    intake.discard(token, actor.user_id)
    return {'discarded': True}


@router.get('/drafts/{did}/original')
def original_document(did: int, actor: Identity = Depends(require_governance), db: Session = Depends(workflow_db)):
    draft(db, did, actor)
    event = db.query(Event).filter(Event.draft_id == did, Event.action == 'created').first()
    metadata = json.loads(event.snapshot_json).get('original_document') if event else None
    if not metadata or not metadata.get('retained'):
        fail(404, 'The original document is not available.')
    try:
        root = intake.storage_root()
        path = (root / metadata['key']).resolve() if root else None
        if not path or path.parent != root or not path.is_file(): raise OSError('Original unavailable')
    except OSError:
        fail(503, 'The original document is temporarily unavailable.')
    return FileResponse(path, filename=metadata['filename'], media_type='application/octet-stream',
        headers={'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'})
