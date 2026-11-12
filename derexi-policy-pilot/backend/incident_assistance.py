"""Human-confirmed support handoff. No startup DDL, worker or outbound defaults.

SMTP acceptance is not delivery or ticket creation. Ambiguous sends never retry
automatically. Tables are installed only through a separately approved migration.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import smtplib
import ssl
import uuid
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictBool
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import TechnicalRoute, RoutingGrant, SupportRequest, SupportAudit, IncidentReport, Department, User
from security import Identity, get_identity, require_admin

router = APIRouter(tags=['incident assistance'])
GUIDANCE = ('If compromise is suspected, stop interacting with suspicious content, do not approve unexpected MFA prompts, '
            'and contact your institution’s established IT/Security reporting channel immediately. '
            'For a lost device, report the loss promptly. Follow your incident procedure; do not investigate or delete evidence. '
            'Do not wait for DeRexi or share passwords, MFA codes, recovery codes or customer account details.')
QUESTIONS = {
    'phishing': ['Did you open a link or attachment, or enter credentials? Answer yes/no only, never the credentials.',
                 'When did this happen and which work application was involved?'],
    'compromise': ['Are you seeing unexpected sign-ins or MFA prompts? Do not share codes.',
                   'Which work application or device is affected, and when did this start?'],
    'lost_device': ['What type of work device is missing, and when was it last seen?',
                    'Could someone else access the unlocked device? Do not share unlock codes.'],
    'outage': ['Which work service is affected and how many people appear affected?',
               'When did the disruption begin, and what error is visible? Omit sensitive details.'],
    'technical': ['Which work device or application is affected?',
                  'When did it start, and what work is blocked? Omit sensitive details.']}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class Intake(StrictModel):
    text: str = Field(min_length=2, max_length=2000)


def protect(value):
    # Reject common explicit secret assignments before persistence/AI. This is
    # defense in depth, not comprehensive DLP; never echo rejected values.
    if re.search(r'(?i)(?:password|passcode|mfa\s*code|otp|recovery\s*code|api[_ -]?key)\s*(?:is|=|:)\s*(?!compromised\b|stolen\b|exposed\b|locked\b|not\b)\S+', value) or re.search(r'\b\d{13,19}\b', value):
        raise HTTPException(422, 'Remove credentials, codes and account numbers before continuing.')
    if any(ord(c) < 32 and c not in '\n\t' for c in value):
        raise HTTPException(422, 'Remove unsupported control characters.')
    return value


def classify(value, use_ai=True):
    protect(value)
    t = value.lower()
    hypothetical = bool(re.search(r'\b(policy|procedure|how (?:do|should|would)|what (?:is|should)|if i|training|hypothetical)\b', t))
    actual = bool(re.search(r"\b(i (?:just |have |accidentally |already )?(?:lost|clicked|opened|entered|received|cannot|can.t)|my .{0,35}(?:stolen|missing|locked|hacked|not working)|we (?:are|have)|is down|are down|currently|right now|unexpected .{0,15}(?:sign.ins|mfa))\b", t))
    kinds = [('lost_device', r'lost|stolen|missing.*(?:laptop|phone|device)'),
             ('phishing', r'phish|suspicious (?:email|message)|clicked|entered.*(?:password|credentials)'),
             ('compromise', r'hack|compromis|ransomware|malware|unexpected.*(?:mfa|sign.in)|unauthori[sz]ed'),
             ('outage', r'outage|(?:service|system|network|application|banking).*(?:down|unavailable)|cannot (?:log|sign)'),
             ('technical', r'not working|error|crash|printer|cannot|can.t')]
    kind = next((k for k, pattern in kinds if re.search(pattern,t)), None)
    incident = bool(kind and (actual or not hypothetical))
    # Existing AI provider configuration is reused, but classification has its
    # own opt-in. A model cannot suppress deterministic high-risk guidance.
    if not incident and not hypothetical and use_ai:
        from ai import classify_support_event
        proposal = classify_support_event(value)
        if proposal in QUESTIONS:
            kind, incident = proposal, True
    urgent = bool(incident and (kind in {'phishing','compromise','lost_device'} or re.search(r'critical|banking.*down|all users',t)))
    return {'potential_incident': incident, 'incident_type': kind if incident else None,
            'urgency': 'urgent' if urgent else 'normal', 'channel': 'security' if kind in {'phishing','compromise','lost_device'} else 'it',
            'guidance': GUIDANCE if urgent else 'Do not share secrets. Follow your institution’s existing reporting process if work is disrupted.',
            'questions': QUESTIONS[kind] if incident else []}


class Prepare(StrictModel):
    idempotency_key: uuid.UUID
    incident_type: Literal['phishing','compromise','lost_device','outage','technical']
    details: str = Field(min_length=5, max_length=2000)
    answers: list[str] = Field(min_length=2, max_length=2)


class Confirm(StrictModel):
    confirmed: StrictBool


class RouteChange(StrictModel):
    department_id: int = Field(gt=0)
    channel: Literal['it','security']
    mailbox_key: str = Field(min_length=1, max_length=80, pattern=r'^[a-zA-Z0-9_-]+$')
    enabled: StrictBool
    expected_revision: int = Field(ge=0)


class GrantChange(StrictModel):
    user_id: int = Field(gt=0)
    department_id: int = Field(gt=0)
    enabled: StrictBool


def workspace(db: Session = Depends(get_db)):
    try:
        yield db
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(503, 'Support routing is temporarily unavailable. Use your established IT/Security channel.')


def audit(db, actor, action, rid=None):
    db.add(SupportAudit(actor_id=actor.user_id, request_id=rid, action=action))


def registry():
    try:
        data = json.loads(os.getenv('DEREXI_APPROVED_MAILBOXES','{}'))
        if not isinstance(data,dict): raise ValueError()
        for key, item in data.items():
            if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',key) or set(item) != {'address','label','channel'}: raise ValueError()
            if item['channel'] not in {'it','security'}: raise ValueError()
            if not re.fullmatch(r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+',item['address']): raise ValueError()
            if not isinstance(item['label'],str) or not 1 <= len(item['label']) <= 100 or '\n' in item['label'] or '\r' in item['label']: raise ValueError()
        return data
    except (ValueError,TypeError,KeyError):
        raise HTTPException(503, 'Approved destinations are unavailable.')


def route_for(db, department, channel):
    rows = db.query(TechnicalRoute).filter_by(department_id=department,channel=channel,enabled=True).all()
    if len(rows) != 1: raise HTTPException(409,'No unique approved route is available. Contact your established IT/Security channel.')
    route = rows[0]
    box = registry().get(route.mailbox_key)
    if not box or box['channel'] != channel: raise HTTPException(409,'This destination needs administrator review.')
    signature = digest([route.id,route.revision,route.mailbox_key,box])
    return route, box, signature


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def utc(value):
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)


def managed_departments(db, actor):
    if actor.is_admin: return None
    ids = {g.department_id for g in db.query(RoutingGrant).filter_by(user_id=actor.user_id)}
    if not ids: raise HTTPException(403,'Technical Routing permission required')
    return ids


def permitted(departments, department):
    if departments is not None and department not in departments: raise HTTPException(403,'Department routing permission required')


@router.post('/support/assess')
def assess(payload: Intake, actor: Identity = Depends(get_identity)):
    return classify(payload.text)


@router.get('/technical-routing/capabilities')
def capabilities(actor: Identity = Depends(get_identity), db: Session = Depends(workspace)):
    if actor.is_admin: return {'can_manage':True,'can_delegate':True}
    return {'can_manage':bool(db.query(RoutingGrant).filter_by(user_id=actor.user_id).first()),'can_delegate':False}


@router.get('/technical-routing/config')
def configuration(actor: Identity = Depends(get_identity), db: Session = Depends(workspace)):
    scope = managed_departments(db,actor)
    routes = db.query(TechnicalRoute)
    departments = db.query(Department)
    if scope is not None:
        routes=routes.filter(TechnicalRoute.department_id.in_(scope)); departments=departments.filter(Department.id.in_(scope))
    return {'outbound_mode': 'smtp' if outbound_enabled() else 'off',
            'mailboxes':[{'key':key,'label':box['label'],'channel':box['channel']} for key,box in registry().items()],
            'departments':[{'id':d.id,'name':d.name} for d in departments],
            'routes':[{'id':r.id,'department_id':r.department_id,'channel':r.channel,'mailbox_key':r.mailbox_key,'enabled':r.enabled,'revision':r.revision} for r in routes],
            'can_delegate':actor.is_admin,
            'people':[{'id':u.id,'name':u.first_name+' '+u.last_name} for u in db.query(User)] if actor.is_admin else [],
            'grants':[{'user_id':g.user_id,'department_id':g.department_id} for g in db.query(RoutingGrant)] if actor.is_admin else []}


@router.post('/technical-routing/config')
def configure(payload: RouteChange, actor: Identity = Depends(get_identity), db: Session = Depends(workspace)):
    permitted(managed_departments(db,actor),payload.department_id)
    if not db.get(Department,payload.department_id): raise HTTPException(422,'Choose an existing department')
    box=registry().get(payload.mailbox_key)
    if not box or box['channel']!=payload.channel: raise HTTPException(422,'Choose an approved destination for this channel')
    row=db.query(TechnicalRoute).filter_by(department_id=payload.department_id,channel=payload.channel).with_for_update().first()
    if row:
        if row.revision!=payload.expected_revision: raise HTTPException(409,'Routing changed; refresh before saving')
        row.mailbox_key=payload.mailbox_key; row.enabled=payload.enabled
    else:
        if payload.expected_revision!=0: raise HTTPException(409,'Refresh the routing configuration')
        row=TechnicalRoute(department_id=payload.department_id,channel=payload.channel,mailbox_key=payload.mailbox_key,enabled=payload.enabled);db.add(row)
    db.flush();audit(db,actor,'route_changed','route:'+str(row.id)+':v'+str(row.revision));db.commit()
    return {'saved':True,'revision':row.revision}


@router.post('/technical-routing/grants')
def delegate(payload: GrantChange, actor: Identity = Depends(require_admin), db: Session = Depends(workspace)):
    if not db.get(User,payload.user_id) or not db.get(Department,payload.department_id): raise HTTPException(422,'Choose an existing employee and department')
    row=db.query(RoutingGrant).filter_by(user_id=payload.user_id,department_id=payload.department_id).first()
    if payload.enabled and not row: db.add(RoutingGrant(user_id=payload.user_id,department_id=payload.department_id))
    if not payload.enabled and row: db.delete(row)
    audit(db,actor,'routing_permission_changed','grant:'+str(payload.user_id)+':'+str(payload.department_id)+':'+str(payload.enabled));db.commit()
    return {'saved':True}


@router.post('/support/prepare')
def prepare(payload: Prepare, actor: Identity = Depends(get_identity), db: Session = Depends(workspace)):
    protect(payload.details)
    for answer in payload.answers:
        if not 1<=len(answer)<=1000: raise HTTPException(422,'Complete both follow-up answers, within 1,000 characters each')
        protect(answer)
    if not actor.department_id: raise HTTPException(409,'Your department needs administrator review')
    assessment=classify(payload.details+' '+' '.join(payload.answers),use_ai=False)
    # A user may explicitly request technical assistance even without a strong
    # indicator, but cannot downgrade a detected high-risk event to an IT route.
    kind=assessment['incident_type'] if assessment['potential_incident'] and assessment['channel']=='security' else payload.incident_type
    channel='security' if kind in {'phishing','compromise','lost_device'} else 'it'
    route,box,signature=route_for(db,actor.department_id,channel)
    data={'employee_id':actor.user_id,'employee':actor.full_name,'email':actor.email,
          'department_id':actor.department_id,'department':db.get(Department,actor.department_id).name,
          'incident_type':kind,'details':payload.details,'answers':payload.answers,
          'urgency':'urgent' if channel=='security' or assessment['urgency']=='urgent' else 'normal',
          'destination':box['label'],'channel':channel}
    key=str(payload.idempotency_key)
    hashed=digest(data)
    old=db.get(SupportRequest,key)
    if old:
        if old.user_id!=actor.user_id: raise HTTPException(404,'Support request not found')
        if old.content_hash!=hashed: raise HTTPException(409,'This request key is already used. Review a new draft.')
        return describe(old)
    row=SupportRequest(id=key,user_id=actor.user_id,department_id=actor.department_id,payload_json=json.dumps(data),
                       content_hash=hashed,route_id=route.id,route_hash=signature,state='draft',attempts=0)
    db.add(row);audit(db,actor,'support_prepared',key)
    try: db.commit()
    except IntegrityError:
        db.rollback();raise HTTPException(409,'Request already exists. Refresh before continuing.')
    return describe(row)


def describe(row):
    return {'id':row.id,'state':row.state,'attempts':row.attempts,'incident_id':row.incident_id,
            'created_at':row.created_at.isoformat(),'request':json.loads(row.payload_json),
            'delivery_notice':'SMTP acceptance is not confirmation of delivery or ticket creation. Investigation stays in your institution’s ticketing system.'}


def owned(db,rid,actor):
    row=db.get(SupportRequest,str(rid))
    if not row or not (actor.is_admin or row.user_id==actor.user_id): raise HTTPException(404,'Support request not found')
    return row


@router.get('/support/requests')
def requests(actor: Identity = Depends(get_identity), db: Session = Depends(workspace)):
    rows=db.query(SupportRequest).filter_by(user_id=actor.user_id).order_by(SupportRequest.created_at.desc()).limit(30)
    return [describe(row) for row in rows]


@router.get('/support/requests/{rid}')
def request_status(rid: uuid.UUID, actor: Identity = Depends(get_identity), db: Session = Depends(workspace)):
    return describe(owned(db,rid,actor))


@router.post('/support/requests/{rid}/confirm')
def confirm(rid: uuid.UUID, payload: Confirm, actor: Identity = Depends(get_identity), db: Session = Depends(workspace)):
    if payload.confirmed is not True: raise HTTPException(422,'Explicit confirmation is required')
    row=owned(db,rid,actor)
    if row.user_id!=actor.user_id: raise HTTPException(403,'Only the employee can confirm their request')
    if row.state!='draft': return describe(row)
    if datetime.now(timezone.utc)-utc(row.created_at)>timedelta(hours=24):
        raise HTTPException(409,'This draft has expired. Prepare and review a new request.')
    data=json.loads(row.payload_json)
    if row.department_id!=actor.department_id or data['email']!=actor.email or data['employee']!=actor.full_name:
        raise HTTPException(409,'Your identity changed. Prepare and review a new request.')
    _,_,signature=route_for(db,row.department_id,data['channel'])
    if signature!=row.route_hash: raise HTTPException(409,'Routing changed. Prepare and review a new request.')
    changed=db.execute(update(SupportRequest).where(SupportRequest.id==row.id,SupportRequest.state=='draft').values(state='queued')).rowcount
    if changed!=1: db.rollback();return describe(owned(db,rid,actor))
    incident=IncidentReport(reporter_id=actor.user_id,description='Support reference '+row.id+'\n'+data['details'],
                            severity='high' if data['urgency']=='urgent' else 'medium',status='reported')
    db.add(incident);db.flush();row.incident_id=incident.id
    audit(db,actor,'support_confirmed',row.id);db.commit()
    # Existing incident notification/triage count sees this record. No fake
    # clarification thread or investigation/resolution is created here.
    return describe(row)


def outbound_enabled():
    return os.getenv('DEREXI_OUTBOUND_EMAIL','off')=='smtp'


class DisabledTransport:
    def send(self, target, subject, body, message_id): return 'disabled'


class SMTPTransport:
    def send(self,target,subject,body,message_id):
        host=os.getenv('DEREXI_SMTP_HOST','');sender=os.getenv('DEREXI_SMTP_FROM','')
        if not host or not re.fullmatch(r'[^\s<>@\r\n]+@[^\s<>@\r\n]+\.[^\s<>@\r\n]+',sender): return 'configuration_error'
        # Only implicit TLS, CA + hostname verification; no STARTTLS downgrade.
        smtp=None
        try:
            smtp=smtplib.SMTP_SSL(host,port=465,timeout=10,context=ssl.create_default_context())
            username=os.getenv('DEREXI_SMTP_USERNAME');password=os.getenv('DEREXI_SMTP_PASSWORD')
            if username: smtp.login(username,password or '')
        except (OSError,smtplib.SMTPException):
            if smtp:
                try:smtp.close()
                except OSError:pass
            return 'retryable'
        message=EmailMessage();message['From']=sender;message['To']=target
        message['Subject']=subject;message['Message-ID']=message_id;message.set_content(body)
        try:
            refused=smtp.send_message(message,from_addr=sender,to_addrs=[target])
            outcome='rejected' if refused else 'accepted'
        except smtplib.SMTPRecipientsRefused: outcome='rejected'
        except (OSError,smtplib.SMTPException): outcome='unknown'
        finally:
            try:smtp.close()
            except OSError:pass
        return outcome


def transport(): return SMTPTransport() if outbound_enabled() else DisabledTransport()


@router.post('/support/requests/{rid}/dispatch')
def dispatch(rid: uuid.UUID, actor: Identity = Depends(get_identity), db: Session = Depends(workspace)):
    row=owned(db,rid,actor)
    if row.state not in {'queued','disabled','retryable','configuration_error'}: return describe(row)
    if row.attempts>=3: raise HTTPException(409,'Retry limit reached. Contact IT/Security with this reference.')
    if row.next_attempt and utc(row.next_attempt)>datetime.now(timezone.utc): raise HTTPException(429,'Please wait before retrying')
    data=json.loads(row.payload_json)
    _,box,signature=route_for(db,row.department_id,data['channel'])
    if row.route_hash!=signature: raise HTTPException(409,'Routing changed. Contact your established IT/Security channel; do not resend.')
    adapter=transport()
    if isinstance(adapter,DisabledTransport):
        db.execute(update(SupportRequest).where(SupportRequest.id==row.id,SupportRequest.state==row.state,
                   SupportRequest.attempts==row.attempts).values(state='disabled'))
        audit(db,actor,'delivery_disabled',row.id);db.commit();db.refresh(row);return describe(row)
    # Persist claim before external I/O. Concurrent dispatches lose this CAS.
    state=row.state
    changed=db.execute(update(SupportRequest).where(SupportRequest.id==row.id,SupportRequest.state==state,
                      SupportRequest.attempts==row.attempts).values(state='sending',attempts=row.attempts+1)).rowcount
    if changed!=1:db.rollback();return describe(owned(db,rid,actor))
    audit(db,actor,'delivery_started',row.id);db.commit();db.refresh(row)
    body=json.dumps({**data,'created_at':row.created_at.isoformat(),'reference':row.id},indent=2)
    try: outcome=adapter.send(box['address'],'DeRexi support request '+row.id,body,'<'+row.id+'@derexi.invalid>')
    except Exception: outcome='unknown'  # provider text is never logged/returned
    if outcome not in {'accepted','rejected','retryable','unknown','configuration_error'}:outcome='unknown'
    row.state=outcome
    row.next_attempt=datetime.now(timezone.utc)+timedelta(seconds=30*(2**(row.attempts-1))) if outcome=='retryable' else None
    audit(db,actor,'delivery_'+outcome,row.id);db.commit()
    return describe(row)


class RouteTest(StrictModel):
    department_id: int = Field(gt=0)
    channel: Literal['it','security']
    confirmed: StrictBool


@router.post('/technical-routing/test')
def test_route(payload: RouteTest, actor: Identity = Depends(get_identity), db: Session = Depends(workspace)):
    permitted(managed_departments(db,actor),payload.department_id)
    if not payload.confirmed:raise HTTPException(422,'Confirm route validation')
    _,box,_=route_for(db,payload.department_id,payload.channel)
    # Configuration validation never sends mail. Delivery testing uses the same
    # review/confirm/outbox workflow, with a mock adapter in isolated tests.
    audit(db,actor,'route_validated');db.commit()
    return {'valid':True,'destination':box['label'],'outbound_enabled':outbound_enabled(),
            'notice':'Configuration validated; no email sent. Delivery testing requires separate authorization.'}


@router.get('/technical-routing/readiness')
def readiness(actor: Identity = Depends(require_admin), db: Session = Depends(workspace)):
    from readiness import configuration_readiness, governance_capacity
    return {'configuration':configuration_readiness(),'owner_coverage':governance_capacity(db),
            'notice':'Read-only configuration and owner inventory. Provider, transport and live acceptance remain separately verified.'}
