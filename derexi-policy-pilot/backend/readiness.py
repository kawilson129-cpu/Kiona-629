"""Read-only readiness helpers. No provider, account creation, DDL or grant changes."""
import os
from sqlalchemy import text


def governance_capacity(db):
    rows=db.execute(text("""SELECT d.id,d.name,count(u.id) AS owner_count
        FROM departments d LEFT JOIN users u ON u.department_id=d.id AND u.role_id IN
        (SELECT id FROM roles WHERE name='Policy Owner')
        GROUP BY d.id,d.name ORDER BY d.id""")).mappings().all()
    return [{'department_id':r['id'],'department':r['name'],'owners':r['owner_count'],
             'ready':r['owner_count']>=2} for r in rows]


def configuration_readiness():
    import session_auth
    import dev_auth
    from transport import protected_database_url
    from incident_assistance import registry, outbound_enabled
    from document_intake import capabilities
    checks=[]
    def result(name,state):checks.append({'item':name,'state':state})
    result('Provider configuration', 'CONFIGURED_UNVERIFIED' if session_auth.public_configuration()['sign_in_enabled'] else 'PENDING')
    result('Developer isolation', 'LOCAL_OPT_IN' if dev_auth.dev_auth_enabled() else 'DISABLED')
    try:
        value=os.getenv('DATABASE_URL','')
        protected_database_url(value)
        result('Database transport configuration','CONFIGURED_UNVERIFIED')
    except Exception:result('Database transport configuration','PENDING')
    try:result('Approved mailbox registry','CONFIGURED_UNVERIFIED' if registry() else 'PENDING')
    except Exception:result('Approved mailbox registry','PENDING')
    result('Outbound email','ENABLED_UNVERIFIED' if outbound_enabled() else 'OFF')
    result('Private original storage','CONFIGURED_UNVERIFIED' if capabilities()['original_retention'] else 'NOT_CONFIGURED')
    for item in ['Live Auth/session acceptance','Direct-client RLS/grant denials','TLS certificates/internal DB transport',
                 'Provider encryption/backups/restore','Durable log retention','Native alternate platforms','Live stakeholder UAT']:
        result(item,'PENDING_EXTERNAL_VERIFICATION')
    return checks
