"""Deployment metadata only, inside a read-only transaction. Never signs anyone in."""
import json
import os
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
from database import DATABASE_URL
from session_auth import public_configuration

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'semester_5/DeRexi_Week 9/evidence'
report={'mode':'SELECT-only metadata; explicit read-only transaction','blocked':[],
        'sign_in_configured':public_configuration()['sign_in_enabled'],
        'database_sslmode':make_url(DATABASE_URL).query.get('sslmode'),
        'unverified':['Production browser HTTPS/certificate','Provider disk and backup encryption',
                      'Live password sign-in/refresh/logout','Direct client role integration tests',
                      'Durable security-log retention and alerting']}
report['env_git_ignored']=subprocess.run(['git','check-ignore','-q','derexi-policy-pilot/backend/.env'],cwd=ROOT).returncode==0
engine=create_engine(DATABASE_URL,connect_args={'connect_timeout':6,'options':'-c default_transaction_read_only=on -c statement_timeout=8000'})
try:
    with engine.connect() as c:
        c.execute(text('SET TRANSACTION READ ONLY'))
        report['transaction_read_only']=c.execute(text('SHOW transaction_read_only')).scalar()
        assert report['transaction_read_only']=='on'
        info=c.connection.driver_connection.info
        report['client_tls']={'encrypted':info.ssl_in_use,**{k:info.ssl_attribute(k) for k in ['protocol','cipher','key_bits']}}
        report['postgres_backend_tls']=dict(c.execute(text('SELECT ssl,version,cipher,bits FROM pg_stat_ssl WHERE pid=pg_backend_pid()')).mappings().one())
        report['backend_role']=dict(c.execute(text('SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user')).mappings().one())
        report['rls_tables']=[dict(r) for r in c.execute(text("""SELECT c.relname AS name,c.relrowsecurity AS enabled,c.relforcerowsecurity AS forced
            FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' ORDER BY c.relname""")).mappings()]
        report['rls_policies']=[dict(r) for r in c.execute(text("""SELECT tablename,policyname,permissive,roles::text AS roles,cmd,qual,with_check
            FROM pg_policies WHERE schemaname='public' ORDER BY tablename,policyname""")).mappings()]
        report['direct_client_grants']=[dict(r) for r in c.execute(text("""SELECT table_name,grantee,privilege_type FROM information_schema.role_table_grants
            WHERE table_schema='public' AND grantee IN ('anon','authenticated','PUBLIC') ORDER BY table_name,grantee,privilege_type""")).mappings()]
        report['public_security_definers']=[dict(r) for r in c.execute(text("""SELECT p.proname AS name,p.prosecdef AS security_definer
            FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.prosecdef ORDER BY p.proname""")).mappings()]
        report['governance_tables_ready']=c.execute(text("SELECT to_regclass('public.governance_drafts') IS NOT NULL AND to_regclass('public.governance_events') IS NOT NULL")).scalar()
        report['business_counts']=dict(c.execute(text('SELECT (SELECT count(*) FROM users) AS users,(SELECT count(*) FROM policies) AS policies,(SELECT count(*) FROM policy_versions) AS versions')).mappings().one())
        report['auth_user_count']=c.execute(text('SELECT count(*) FROM auth.users')).scalar()
        c.rollback()
except Exception as exc:
    report['blocked'].append(type(exc).__name__+': metadata check unavailable; connection details suppressed')
finally: engine.dispose()
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'live-readonly-security.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['rls_policies','direct_client_grants']},indent=2))
sys.exit(2 if report['blocked'] else 0)
