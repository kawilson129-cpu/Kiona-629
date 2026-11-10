"""SELECT-only Week 8 inventory. Never prints credentials or employee email."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import create_engine, text
from database import DATABASE_URL

report = {'mode': 'explicit read-only transaction', 'departments': [], 'blocked': []}
engine = create_engine(DATABASE_URL, connect_args={'connect_timeout': 8,
    'options': '-c default_transaction_read_only=on -c statement_timeout=8000'})
try:
    with engine.connect() as c:
        c.execute(text('SET TRANSACTION READ ONLY'))
        assert c.execute(text('SHOW transaction_read_only')).scalar() == 'on'
        report['departments'] = [dict(r) for r in c.execute(text("""
            SELECT d.id, d.name, count(u.id) FILTER (WHERE r.name='Policy Owner') AS owner_count,
              greatest(0, 2-count(u.id) FILTER (WHERE r.name='Policy Owner')) AS missing
            FROM departments d LEFT JOIN users u ON u.department_id=d.id
            LEFT JOIN roles r ON r.id=u.role_id GROUP BY d.id,d.name ORDER BY d.id
        """)).mappings()]
        report['roles'] = [dict(r) for r in c.execute(text('SELECT id,name FROM roles ORDER BY id')).mappings()]
        report['ownership'] = [dict(r) for r in c.execute(text("""
            SELECT u.id,u.first_name,u.last_name,u.department_id,r.name AS role,count(p.id) AS policies
            FROM users u JOIN roles r ON r.id=u.role_id LEFT JOIN policies p ON p.owner_id=u.id
            GROUP BY u.id,r.name ORDER BY u.id
        """)).mappings()]
        report['columns'] = [dict(r) for r in c.execute(text("""
            SELECT table_name,column_name,data_type FROM information_schema.columns
            WHERE table_schema='public' AND table_name IN ('users','policies','policy_versions','departments')
            ORDER BY table_name,ordinal_position
        """)).mappings()]
        c.rollback()
except Exception as exc:
    report['blocked'].append(type(exc).__name__ + ': inventory unavailable; connection details suppressed')
finally:
    engine.dispose()
out = Path(__file__).resolve().parents[2] / 'docs/week8/evidence/inventory.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
