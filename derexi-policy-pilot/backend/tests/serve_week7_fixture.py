"""Local browser fixture: real API + ephemeral SQLite, never Supabase.

Run: ../.venv/bin/python tests/serve_week7_fixture.py
Open http://127.0.0.1:8027/ui/?as=8#messages (all data is illustrative).
"""
import sys
from threading import Lock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from messaging_fixture import isolated_database
import main
from database import get_db
from models import Conversation, Message, PolicyCitation, ClarificationRequest, ClarificationReply

engine, factory = isolated_database()
request_lock = Lock()  # SQLite's one in-memory connection cannot serve parallel transactions.
factory.configure(bind=engine)
with factory() as db:
    for i, (uid, assignee, status, question, reason) in enumerate([
        (8, 9, 'in_progress', 'How do I request an accommodation?', 'My manager is remote and cannot sign the form.'),
        (8, 9, 'open', 'When should I submit my leave request?', 'Can my manager approve this while travelling?'),
        (8, 9, 'resolved', 'Where can I find the parental leave form?', 'I need the current version of the form.'),
        (3, None, 'open', 'Who owns the travel guidance?', 'No owner is listed. Please route my question.'),
        (5, 12, 'open', 'What approvals are required for client documentation?', 'An unrelated employee thread for access checks.')
    ], 1):
        conv = Conversation(user_id=uid, topic=question, status='open')
        db.add(conv); db.flush()
        msg = Message(conversation_id=conv.id, sender='user', body=question)
        answer = Message(conversation_id=conv.id, sender='derexi', body='Review Employee Leave and contact the assigned policy owner for guidance specific to your situation.')
        db.add_all([msg, answer]); db.flush()
        db.add(PolicyCitation(message_id=answer.id, policy_version_id=2, excerpt='Submit a leave request through the employee portal.'))
        thread = ClarificationRequest(id=i, conversation_id=conv.id, message_id=msg.id,
            user_id=uid, assigned_to=assignee, policy_id=48 if assignee else None,
            status=status, reason=reason)
        db.add(thread); db.flush()
        if i == 1:
            db.add(ClarificationReply(request_id=i, sender_id=9,
                body='Use the electronic signature workflow. Your manager can review and sign remotely; contact HR if the form link has expired.'))
    db.commit()


def fixture_db():
    with request_lock, factory() as db:
        yield db


main.app.dependency_overrides[get_db] = fixture_db

if __name__ == '__main__':
    import uvicorn
    print('ISOLATED BROWSER FIXTURE — all records are illustrative; no Supabase access')
    uvicorn.run(main.app, host='127.0.0.1', port=8027, proxy_headers=False, access_log=False)
