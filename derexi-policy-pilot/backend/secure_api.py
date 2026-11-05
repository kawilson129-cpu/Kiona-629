"""Authenticated API assembly over the existing application handlers.

No developer identity fallback exists here. The legacy main:app entry point is
kept separate until the developer has an approved local demo data source.
"""
from __future__ import annotations

import inspect
from dataclasses import asdict
from functools import wraps
from typing import get_type_hints

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.routing import APIRoute
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import and_, or_, func

import main
import models as m
import rbac as r
from auth import AuthenticationError, SupabaseJWTVerifier
from principals import BusinessUser, PrincipalResolver, PrincipalResolutionError
from schemas import PolicyStatusUpdate

bearer = HTTPBearer(auto_error=False)


def business_user(db, uid):
    user = db.get(m.User, uid)
    if user is None or user.role is None:
        return None
    return BusinessUser(user.id, user.role_id, user.role.name, user.department_id)


def require_verified_token(request: Request, credential: HTTPAuthorizationCredentials = Depends(bearer)):
    # Verify before acquiring a database session; anonymous requests need no DB.
    if credential is None:
        raise HTTPException(401, "Sign in to continue", headers={"WWW-Authenticate": "Bearer"})
    authorization = "Bearer " + credential.credentials
    try:
        request.app.state.verifier.verify(credential.credentials)
    except AuthenticationError:
        raise HTTPException(401, "Invalid or expired credentials", headers={"WWW-Authenticate": "Bearer"}) from None
    return authorization


def require_authentication(request: Request, authorization=Depends(require_verified_token), db=Depends(main.get_db)):
    # Reuse the Stage 1 resolver; token roles/IDs never become business authority.
    resolver = PrincipalResolver(request.app.state.verifier, request.app.state.subject_mapping,
                                 lambda uid: business_user(db, uid))
    try:
        return resolver.resolve(authorization)
    except AuthenticationError:
        raise HTTPException(401, "Invalid or expired credentials") from None
    except PrincipalResolutionError:
        raise HTTPException(403, "This identity is not authorized for DeRexi") from None


def allowed(condition, private=False):
    if not condition:
        raise HTTPException(404 if private else 403,
                            "Record not found" if private else "You do not have permission for this action")


def record(db, model, uid):
    item = db.get(model, uid)
    if item is None:
        raise HTTPException(404, "Record not found")
    return item


def policy_scope(policy):
    return r.PolicyScope(policy.owner_id, policy.status)


def thread_scope(thread):
    return r.ClarificationScope(thread.id, thread.user_id, thread.assigned_to, thread.status, thread.policy_id)


def visible_policies(p):
    if r.is_admin(p):
        return m.Policy.id.is_not(None)
    if p.role is r.Role.POLICY_OWNER:
        return or_(m.Policy.status == "approved", m.Policy.owner_id == p.user_id)
    return m.Policy.status == "approved"


REFERENCE = {"list_departments", "list_roles", "list_incident_categories", "search_policies", "pulse_feed", "pulse_health"}
ACTIONS = REFERENCE | {"health", "list_users", "list_policy_categories", "list_policies", "get_policy",
    "create_policy", "add_policy_version", "ask", "get_conversation", "list_clarifications",
    "create_clarification", "get_clarification", "add_clarification_reply", "resolve_clarification",
    "list_incidents", "create_incident", "update_incident", "create_feedback", "policy_health"}


def dispatch(endpoint, p, args):
    name = endpoint.__name__
    db = args.get("db")
    payload = args.get("payload")
    # Scope collections before serialization. Query filters can only narrow it.
    if name == "list_policies":
        query = db.query(m.Policy).filter(visible_policies(p))
        for key in ("status", "category_id"):
            if args.get(key) is not None:
                query = query.filter(getattr(m.Policy, key) == args[key])
        return [main.policy_to_dict(item, db) for item in query.order_by(m.Policy.id).all()]
    if name == "list_policy_categories":
        rows = db.query(m.PolicyCategory.id, m.PolicyCategory.name, func.count(m.Policy.id)).outerjoin(
            m.Policy, and_(m.Policy.category_id == m.PolicyCategory.id, visible_policies(p))
        ).group_by(m.PolicyCategory.id, m.PolicyCategory.name).order_by(m.PolicyCategory.id).all()
        return [{"id": uid, "name": title, "count": count} for uid, title, count in rows]
    if name == "list_clarifications":
        query = db.query(m.ClarificationRequest).filter(or_(
            m.ClarificationRequest.user_id == p.user_id, m.ClarificationRequest.assigned_to == p.user_id))
        for key in ("status", "assigned_to"):
            if args.get(key) is not None:
                query = query.filter(getattr(m.ClarificationRequest, key) == args[key])
        return [main.get_clarification(item.id, db) for item in query.order_by(m.ClarificationRequest.created_at.desc()).all()]
    if name == "list_incidents":
        query = db.query(m.IncidentReport)
        if not r.is_admin(p):
            query = query.filter(or_(m.IncidentReport.reporter_id == p.user_id, m.IncidentReport.assigned_to == p.user_id))
        for key in ("status", "severity", "reporter_id"):
            if args.get(key) is not None:
                query = query.filter(getattr(m.IncidentReport, key) == args[key])
        return [main._incident_dict(item) for item in query.order_by(m.IncidentReport.created_at.desc()).all()]

    if name == "health":
        allowed(r.is_admin(p))
    elif name == "get_policy":
        policy = record(db, m.Policy, args["policy_id"])
        allowed(r.can_read_policy(p, policy_scope(policy)), private=True)
    elif name == "create_policy":
        allowed(r.can_create_policy(p, payload.owner_id or p.user_id, payload.status))
        if payload.version.created_by is not None:
            allowed(r.actor_matches(p, payload.version.created_by))
        args["payload"] = payload.model_copy(update={"owner_id": payload.owner_id or p.user_id,
            "version": payload.version.model_copy(update={"created_by": p.user_id})})
    elif name == "add_policy_version":
        policy = record(db, m.Policy, args["policy_id"])
        allowed(r.can_read_policy(p, policy_scope(policy)), private=True)
        allowed(r.can_edit_policy(p, policy_scope(policy)))
        if payload.created_by is not None:
            allowed(r.actor_matches(p, payload.created_by))
        args["payload"] = payload.model_copy(update={"created_by": p.user_id})
    elif name in ("ask", "create_clarification", "create_feedback"):
        allowed(r.actor_matches(p, payload.user_id))
        args["payload"] = payload.model_copy(update={"user_id": p.user_id})
        if name == "create_clarification":
            conversation = None
            message = None
            if payload.conversation_id is not None:
                conversation = record(db, m.Conversation, payload.conversation_id)
                allowed(r.can_read_conversation(p, r.ConversationScope(conversation.id, conversation.user_id)), private=True)
            if payload.message_id is not None:
                message = record(db, m.Message, payload.message_id)
                linked = record(db, m.Conversation, message.conversation_id)
                allowed(r.can_read_conversation(p, r.ConversationScope(linked.id, linked.user_id)), private=True)
            if payload.policy_id is not None:
                policy = record(db, m.Policy, payload.policy_id)
                allowed(r.can_read_policy(p, policy_scope(policy)), private=True)
                if payload.assigned_to is None:
                    args["payload"] = args["payload"].model_copy(update={"assigned_to": policy.owner_id})
        if name == "create_feedback":
            message = record(db, m.Message, payload.message_id)
            conversation = record(db, m.Conversation, message.conversation_id)
            allowed(r.can_read_conversation(p, r.ConversationScope(conversation.id, conversation.user_id)), private=True)
            allowed(r.can_submit_feedback(p, payload.user_id, r.ConversationScope(conversation.id, conversation.user_id),
                                           r.MessageScope(message.conversation_id, message.sender)))
    elif name == "get_conversation":
        conversation = record(db, m.Conversation, args["conversation_id"])
        allowed(r.can_read_conversation(p, r.ConversationScope(conversation.id, conversation.user_id)), private=True)
    elif name in ("get_clarification", "add_clarification_reply", "resolve_clarification"):
        thread = thread_scope(record(db, m.ClarificationRequest, args["request_id"]))
        allowed(r.can_read_clarification(p, thread), private=True)
        if name == "add_clarification_reply":
            allowed(r.can_reply_clarification(p, thread, payload.sender_id))
            args["payload"] = payload.model_copy(update={"sender_id": p.user_id})
        if name == "resolve_clarification":
            allowed(r.can_resolve_clarification(p, thread))
    elif name == "create_incident":
        allowed(r.can_create_incident(p, payload.reporter_id, payload.assigned_to, payload.escalation_level))
        args["payload"] = payload.model_copy(update={"reporter_id": p.user_id})
    elif name == "update_incident":
        item = record(db, m.IncidentReport, args["incident_id"])
        incident = r.IncidentScope(item.reporter_id, item.assigned_to)
        allowed(r.can_read_incident(p, incident), private=True)
        allowed(r.can_update_incident(p, incident, payload.model_dump(exclude_unset=True)))
    elif name == "policy_health":
        allowed(r.can_read_governance(p))
    result = endpoint(**args)
    if name == "list_users":
        return [{k: v for k, v in user.items() if k != "email"} for user in result]
    return result


def guarded(endpoint):
    # Keep FastAPI's original payload/query validation and response contracts.
    hints = get_type_hints(endpoint)
    @wraps(endpoint)
    def run(**kwargs):
        principal = kwargs.pop("_principal")
        return dispatch(endpoint, principal, kwargs)
    params = [inspect.Parameter("_principal", inspect.Parameter.KEYWORD_ONLY,
                                default=Depends(require_authentication))]
    params += [p.replace(kind=inspect.Parameter.KEYWORD_ONLY, annotation=hints.get(p.name, p.annotation))
               for p in inspect.signature(endpoint).parameters.values()]
    run.__signature__ = inspect.Signature(params, return_annotation=hints.get("return", inspect.Signature.empty))
    return run


def create_app(verifier: SupabaseJWTVerifier, subject_mapping):
    # Validate configuration now. This constructor never creates or seeds a DB.
    if verifier.settings.algorithms != ("ES256",):
        raise ValueError("Only ES256 is supported")
    PrincipalResolver(verifier, subject_mapping, lambda uid: None)
    app = FastAPI(title="DeRexi secured API", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.verifier = verifier
    app.state.subject_mapping = dict(subject_mapping)
    app.exception_handlers.update(main.app.exception_handlers)
    # Newer FastAPI keeps included routers lazy; enumerate the known Pulse
    # router explicitly instead of dropping its protected endpoints.
    seen = set()
    for route in [*main.app.routes, *main.pulse_router.routes]:
        if not isinstance(route, APIRoute) or route.path == "/":
            continue
        key = (route.path, frozenset(route.methods))
        if key in seen:
            continue
        seen.add(key)
        if route.endpoint.__name__ not in ACTIONS:
            raise RuntimeError("Unmapped application route; add an explicit permission rule")
        app.add_api_route(route.path, guarded(route.endpoint), methods=list(route.methods),
                          status_code=route.status_code, name=route.name)

    @app.get("/")
    def service():
        return {"service": "DeRexi secured API"}

    @app.get("/me")
    def me(p=Depends(require_authentication)):
        return asdict(p)

    @app.get("/admin/clarifications")
    def clarification_oversight(p=Depends(require_authentication), db=Depends(main.get_db)):
        allowed(r.is_admin(p))
        return [asdict(r.clarification_oversight(p, thread_scope(t)))
                for t in db.query(m.ClarificationRequest).order_by(m.ClarificationRequest.id).limit(1000).all()]

    @app.patch("/policies/{policy_id}/status")
    def publish(policy_id: int, payload: PolicyStatusUpdate, p=Depends(require_authentication), db=Depends(main.get_db)):
        allowed(r.is_admin(p))
        policy = record(db, m.Policy, policy_id)
        allowed(r.can_set_policy_status(p, policy_scope(policy), payload.status))
        if payload.status == "approved" and not policy.versions:
            raise HTTPException(409, "Add a policy version before publication")
        policy.status = payload.status
        db.commit()
        return {"id": policy.id, "status": policy.status}
    return app
