"""Read-only deployment diagnostics; never runs messaging write operations."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.engine import make_url
from database import DATABASE_URL
from security import identity_from_user_row
from messaging import list_messages, list_notifications

report = {'mode': 'PostgreSQL default_transaction_read_only=on; SELECT only',
          'tls': {}, 'read_models': [], 'blocked': [],
          'unverified': ['Browser HTTPS deployment', 'Database certificate/hostname verification',
                         'Provider storage/backup encryption', 'Direct-client RLS behaviour',
                         'Production Supabase user sign-in']}
report['configured_sslmode'] = make_url(DATABASE_URL).query.get('sslmode', 'unset')
engine = create_engine(DATABASE_URL, connect_args={
    'connect_timeout': 6,
    'options': '-c default_transaction_read_only=on -c statement_timeout=8000'
})
try:
    with engine.connect() as connection:
        # Poolers can reset startup parameters; enforce the transaction itself.
        connection.execute(text('SET TRANSACTION READ ONLY'))
        report['transaction_read_only'] = connection.execute(text('SHOW transaction_read_only')).scalar()
        assert connection.execute(text('SHOW transaction_read_only')).scalar() == 'on'
        info = connection.connection.driver_connection.info
        report['tls'] = {'client_to_pooler_encrypted': info.ssl_in_use,
                         **{key:info.ssl_attribute(key) for key in ('protocol','cipher','key_bits')}}
        tls = connection.execute(text('SELECT ssl, version, cipher, bits FROM pg_stat_ssl WHERE pid=pg_backend_pid()')).mappings().first()
        report['postgres_backend_connection'] = dict(tls) if tls else {'verified': False}
        report['backend_uses_local_socket'] = connection.execute(text('SELECT inet_client_addr() IS NULL')).scalar()
        if not tls or not tls['ssl']:
            report['unverified'].append('Pooler-to-Postgres transport: backend reports no TLS; topology/provider protection unverified')
        has_reads = connection.execute(text("SELECT to_regclass('public.clarification_reads') IS NOT NULL")).scalar()
        report['clarification_reads_exists'] = has_reads
        report['employee_count'] = connection.execute(text('SELECT count(*) FROM public.users')).scalar()
        if not has_reads:
            report['blocked'].append('clarification_reads absent; schema changes require separate authorization')
        else:
            rows = connection.execute(text('''SELECT DISTINCT ON (r.name) u.id, u.first_name, u.last_name,
                    u.email, u.department_id, r.name AS role
                    FROM users u JOIN roles r ON r.id=u.role_id ORDER BY r.name,u.id''')).mappings().all()
            with Session(bind=connection) as db:
                for row in rows:
                    identity = identity_from_user_row(row, 'dev')
                    folder = 'all' if identity.is_admin else 'requests'
                    data = list_messages(folder=folder,q=None,status=None,limit=1,offset=0,identity=identity,db=db)
                    notices = list_notifications(identity=identity,db=db)
                    report['read_models'].append({'role':identity.role,'folder':folder,
                        'list':'PASS','notifications':'PASS','preview_count':len(data['threads']),
                        'counts_nonnegative':notices['unread_total'] >= 0})
        connection.rollback()
except Exception as exc:
    # Database exceptions may embed credentials and SQL; never emit them.
    report['blocked'].append(type(exc).__name__ + ': read-only connection/query unavailable; details suppressed')
finally:
    engine.dispose()

out = Path(__file__).resolve().parents[2] / 'docs/week7/evidence/readonly-diagnostics.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
sys.exit(2 if report['blocked'] else 0)
