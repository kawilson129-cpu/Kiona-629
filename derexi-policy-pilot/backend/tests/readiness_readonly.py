"""Explicit live SELECT-only preflight; no Auth/provider login or record changes.

Never run implicitly with tests. Transaction is READ ONLY and always rolled back.
Only allowlisted metadata/counts are exported; never exception or configuration values.
"""
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
from transport import protected_database_url
load_dotenv(Path(__file__).resolve().parents[1]/'.env')
if '--live-readonly' not in sys.argv:raise SystemExit('Explicit --live-readonly required')
out=Path(os.environ['DEREXI_SPRINT_EVIDENCE'])
report={'mode':'explicit READ ONLY transaction, rolled back','mutations':False}
try:
    engine=create_engine(protected_database_url(os.environ['DATABASE_URL']),connect_args={'connect_timeout':8})
    with engine.connect() as conn:
        tx=conn.begin()
        try:
            conn.execute(text('SET TRANSACTION READ ONLY'))
            conn.execute(text("SET LOCAL statement_timeout = '8000ms'"))
            report['read_only']=conn.execute(text('SHOW transaction_read_only')).scalar()=='on'
            report['owner_coverage']=[dict(r) for r in conn.execute(text("""SELECT d.id AS department_id,d.name AS department,
                count(u.id) AS owners FROM public.departments d LEFT JOIN public.users u
                ON u.department_id=d.id AND u.role_id IN (SELECT id FROM public.roles WHERE name='Policy Owner')
                GROUP BY d.id,d.name ORDER BY d.id""")).mappings()]
            report['owner_coverage_ready']=all(d['owners']>=2 for d in report['owner_coverage'])
            expected=['governance_drafts','governance_events','technical_routes','technical_routing_grants','support_requests','support_audit']
            tables=set(conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).scalars())
            report['required_tables']={name:name in tables for name in expected}
            report['auth_user_count']=conn.execute(text('SELECT count(*) FROM auth.users')).scalar()
            report['rls_tables']=[dict(r) for r in conn.execute(text("SELECT relname,relrowsecurity AS rls_enabled FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' ORDER BY relname")).mappings()]
            report['direct_client_table_grants']=conn.execute(text("SELECT count(*) FROM information_schema.role_table_grants WHERE table_schema='public' AND grantee IN ('PUBLIC','anon','authenticated')")).scalar()
            report['authenticated_select_policies']=conn.execute(text("SELECT count(*) FROM pg_policies WHERE schemaname='public' AND cmd='SELECT' AND 'authenticated'=ANY(roles)")).scalar()
            report['backend_bypasses_rls']=conn.execute(text('SELECT rolbypassrls FROM pg_roles WHERE rolname=current_user')).scalar()
            report['backend_tls']=[dict(r) for r in conn.execute(text('SELECT ssl,version,cipher FROM pg_stat_ssl WHERE pid=pg_backend_pid()')).mappings()]
            report['status']='READ_ONLY_INVENTORY_COMPLETE'
        finally:tx.rollback()
    engine.dispose()
except Exception:
    report['status']='UNAVAILABLE';report['notice']='Read-only inventory could not complete. No provider exception or private configuration is exported.'
(out/'live-readonly-preflight.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'read_only':report.get('read_only'),'mutations':False}))
sys.exit(0 if report['status']=='READ_ONLY_INVENTORY_COMPLETE' else 1)
