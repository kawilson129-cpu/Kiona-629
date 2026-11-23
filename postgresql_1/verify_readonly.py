"""Bounded live SELECT/catalog verification only. No app startup or write SQL.

Uses existing DeRexi connection configuration and transport policy without printing
credentials. Writes sanitized evidence only inside this existing course folder.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
BACKEND = ROOT.parent / 'derexi-policy-pilot/backend'
TABLES = ['departments', 'roles', 'users', 'policies', 'clarification_reads']
QUERIES = {
    'connection': 'SELECT 1 AS connection_check, current_database() AS database_name, '
                  "current_schema() AS schema_name, current_setting('server_version_num') AS server_version_num",
    'columns': """SELECT table_schema, table_name, ordinal_position, column_name,
        data_type, udt_name, is_nullable, column_default, is_identity, identity_generation
        FROM information_schema.columns WHERE table_schema = 'public'
        AND table_name IN ('departments','roles','users','policies','clarification_reads')
        ORDER BY table_name, ordinal_position""",
    'constraints': """SELECT rel.relname AS table_name, c.conname AS constraint_name,
        c.contype AS constraint_type, pg_get_constraintdef(c.oid) AS definition
        FROM pg_constraint c JOIN pg_class rel ON rel.oid = c.conrelid
        JOIN pg_namespace n ON n.oid = rel.relnamespace
        WHERE n.nspname = 'public' AND rel.relname IN
        ('departments','roles','users','policies','clarification_reads')
        AND c.contype IN ('p','f','u','c') ORDER BY rel.relname, c.conname""",
    'counts': """SELECT (SELECT count(*) FROM public.departments) AS departments,
        (SELECT count(*) FROM public.roles) AS roles,
        (SELECT count(*) FROM public.users) AS users,
        (SELECT count(*) FROM public.policies) AS policies""",
    'select': 'SELECT id, name FROM public.departments ORDER BY id;',
    'filter_sort': "SELECT id, title, status FROM public.policies WHERE status = 'approved' ORDER BY title ASC, id ASC LIMIT 5;",
    'join': """SELECT d.name AS department, r.name AS role, count(u.id) AS user_count
FROM public.users AS u
JOIN public.departments AS d ON d.id = u.department_id
JOIN public.roles AS r ON r.id = u.role_id
GROUP BY d.name, r.name
ORDER BY d.name ASC, r.name ASC;""",
}


def run(out):
    report = {'timestamp': datetime.now(timezone.utc).isoformat(), 'status': 'BLOCKED',
              'scope': 'Live PostgreSQL SELECT/catalog queries inside enforced READ ONLY transaction; always rolled back.',
              'mutations_executed': False, 'queries': {}, 'checks': []}
    engine = None
    stage = 'configuration'
    try:
        sys.path.insert(0, str(BACKEND))
        from dotenv import load_dotenv
        from sqlalchemy import create_engine, text
        from sqlalchemy.engine import make_url
        from transport import protected_database_url
        load_dotenv(BACKEND / '.env', override=False)
        url = protected_database_url(os.environ['DATABASE_URL'])
        report['configured_sslmode'] = make_url(url).query.get('sslmode', 'unset')
        engine = create_engine(url, connect_args={'connect_timeout': 8,
            'options': '-c default_transaction_read_only=on -c statement_timeout=8000 -c lock_timeout=2000'})
        stage = 'connection'
        with engine.connect() as conn:
            tx = conn.begin()
            try:
                conn.execute(text('SET TRANSACTION READ ONLY'))
                report['transaction_read_only'] = conn.execute(text('SHOW transaction_read_only')).scalar()
                assert report['transaction_read_only'] == 'on'
                info = conn.connection.driver_connection.info
                report['client_tls'] = {'encrypted': bool(info.ssl_in_use),
                    'protocol': info.ssl_attribute('protocol') if info.ssl_in_use else None}
                for name in ['connection', 'columns', 'constraints']:
                    stage = name
                    rows = [dict(r) for r in conn.execute(text(QUERIES[name])).mappings()]
                    report['queries'][name] = {'sql': QUERIES[name], 'status': 'VERIFIED', 'rows': rows}
                columns = {(r['table_name'], r['column_name']) for r in report['queries']['columns']['rows']}
                expected = {('departments','id'),('departments','name'),('roles','id'),('roles','name'),
                            ('users','id'),('users','role_id'),('users','department_id'),
                            ('policies','id'),('policies','title'),('policies','status')}
                assert expected <= columns
                report['schema_names_verified_before_data_queries'] = True
                for name in ['counts', 'select', 'filter_sort', 'join']:
                    stage = name
                    rows = [dict(r) for r in conn.execute(text(QUERIES[name])).mappings()]
                    report['queries'][name] = {'sql': QUERIES[name], 'status': 'VERIFIED', 'rows': rows}
                values = report['queries']['counts']['rows'][0]
                checks = {
                    'Read-only transaction enforced': report['transaction_read_only'] == 'on',
                    'PostgreSQL responds to SELECT 1': report['queries']['connection']['rows'][0]['connection_check'] == 1,
                    'Real PostgreSQL version reported': int(report['queries']['connection']['rows'][0]['server_version_num']) >= 100000,
                    'Public table/column names verified before examples': expected <= columns,
                    'Four preferred tables have catalog primary keys': all(any(c['table_name'] == t and c['constraint_type'] == 'p'
                        for c in report['queries']['constraints']['rows']) for t in TABLES[:4]),
                    'SELECT returns actual department rows': len(report['queries']['select']['rows']) == values['departments'],
                    'WHERE returns only approved rows within limit': 0 < len(report['queries']['filter_sort']['rows']) <= 5
                        and all(r['status'] == 'approved' for r in report['queries']['filter_sort']['rows']),
                    'JOIN aggregates all users without exporting personal fields': sum(r['user_count'] for r in report['queries']['join']['rows']) == values['users'],
                }
                report['checks'] = [{'name': k, 'status': 'PASS' if v else 'FAIL'} for k, v in checks.items()]
                report['status'] = 'VERIFIED' if all(checks.values()) else 'PARTIAL'
            finally:
                tx.rollback()
                report['transaction_end'] = 'ROLLED BACK'
    except Exception as exc:
        report['blocker'] = {'stage': stage, 'exception_class': type(exc).__name__,
            'message': 'Connection/configuration or read-only query unavailable; private provider details suppressed.'}
    finally:
        if engine is not None:
            engine.dispose()
    report['passed'] = sum(c['status'] == 'PASS' for c in report['checks'])
    report['failed'] = sum(c['status'] == 'FAIL' for c in report['checks'])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, default=str) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'passed', 'failed', 'mutations_executed']}))
    return 0 if report['status'] == 'VERIFIED' else 2


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--live-readonly', action='store_true', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    out = Path(args.output).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        raise SystemExit('Use a new output file strictly inside postgresql_1')
    raise SystemExit(run(out))
