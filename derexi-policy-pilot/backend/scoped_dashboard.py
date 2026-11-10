"""Policy Owner dashboard: departmental policy aggregates, authorized personal data."""
from collections import Counter
from datetime import date, timedelta
from sqlalchemy import exists, func, or_
from models import (Policy, PolicyVersion, User, Conversation, Message, Feedback,
                    PolicyCitation, ClarificationRequest, ClarificationReply, IncidentReport)


def department_health(db, actor):
    policies = db.query(Policy).join(User, User.id == Policy.owner_id).filter(
        User.department_id == actor.department_id).all()
    ids = [p.id for p in policies]
    versions = db.query(PolicyVersion).filter(PolicyVersion.policy_id.in_(ids)).order_by(
        PolicyVersion.created_at.desc(),PolicyVersion.id.desc()).all()
    latest = {}
    for version in versions:
        latest.setdefault(version.policy_id,version)
    reviews = sum(1 for p in policies if p.status == 'approved' and p.id in latest
                  and latest[p.id].requires_review and latest[p.id].review_date
                  and latest[p.id].review_date <= date.today()+timedelta(days=30))
    conversations = db.query(Conversation).filter(Conversation.user_id == actor.user_id).all()
    conversations_ids = [c.id for c in conversations]
    message_count = db.query(Message).filter(Message.conversation_id.in_(conversations_ids)).count()
    requests = db.query(ClarificationRequest).filter(or_(
        ClarificationRequest.user_id == actor.user_id,
        ClarificationRequest.assigned_to == actor.user_id,
        exists().where(ClarificationReply.request_id == ClarificationRequest.id,
                       ClarificationReply.sender_id == actor.user_id))).all()
    incidents = db.query(IncidentReport).filter(or_(IncidentReport.reporter_id == actor.user_id,
                                                   IncidentReport.assigned_to == actor.user_id)).all()
    feedback = db.query(Feedback).join(PolicyCitation,PolicyCitation.message_id == Feedback.message_id).join(
        PolicyVersion,PolicyVersion.id == PolicyCitation.policy_version_id).filter(
        PolicyVersion.policy_id.in_(ids)).distinct().all()
    cited = db.query(Policy.id,Policy.title,func.count(PolicyCitation.id)).join(
        PolicyVersion,PolicyVersion.policy_id == Policy.id).join(
        PolicyCitation,PolicyCitation.policy_version_id == PolicyVersion.id).filter(
        Policy.id.in_(ids)).group_by(Policy.id,Policy.title).order_by(
        func.count(PolicyCitation.id).desc(),Policy.title).limit(5).all()
    def counts(items,key):
        return [{key:k,'count':v} for k,v in sorted(Counter(getattr(x,key) for x in items).items())]
    helpful = sum(1 for f in feedback if f.rating)
    return {'scope':'department','department_id':actor.department_id,
            'conversation_scope':'own','totals':{'policies':len(policies),
                'conversations':len(conversations),'messages':message_count,'incidents':len(incidents)},
            'policies_by_status':counts(policies,'status'),'reviews_due':reviews,
            'clarifications_by_status':counts(requests,'status'),
            'incidents_by_status':counts(incidents,'status'),
            'incidents_by_severity':counts(incidents,'severity'),
            'feedback':{'total':len(feedback),'helpful':helpful,'not_helpful':len(feedback)-helpful,
                        'helpful_rate':round(helpful/len(feedback),3) if feedback else None},
            'top_cited_policies':[{'id':pid,'title':title,'citation_count':count} for pid,title,count in cited]}
