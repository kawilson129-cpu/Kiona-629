"""Offline SQLite fixture for the existing Week 7 HTTP workflow suite.

Runs real route handlers and visibility predicates against actual in-memory
rows. Only PostgreSQL syntax is translated (LATERAL -> correlated subqueries,
casts, ILIKE, DISTINCT ON). PostgreSQL plans, RLS and trigram ranking require
separate verification. No live credentials, writes, sequences or AI calls.
"""
import os
import re
from datetime import datetime, timezone

# Set before importing database/main; .env cannot override these values.
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://offline:offline@127.0.0.1:1/offline'
os.environ['OPENAI_API_KEY'] = ''
os.environ['DEREXI_ENV'] = 'test'
os.environ['DEREXI_DEV_AUTH'] = '1'
os.environ['DEREXI_DEV_USER_IDS'] = ''

import psycopg2
from sqlalchemy import BigInteger, create_engine, event, text
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.elements import TextClause


def blocked_connect(*args, **kwargs):
    raise RuntimeError('Live PostgreSQL connections are forbidden in offline fixtures')


psycopg2.connect = blocked_connect


@compiles(BigInteger, 'sqlite')
def sqlite_integer(type_, compiler, **kwargs):
    return 'INTEGER'


def translate(sql):
    # Preserve the actual visibility, folder and search predicates verbatim.
    if 'LEFT JOIN LATERAL' in sql:
        for field in ('body', 'created_at', 'sender_id'):
            sql = sql.replace('lr.' + field, '(SELECT latest.' + field +
                ' FROM clarification_replies latest WHERE latest.request_id = cr.id'
                ' ORDER BY latest.created_at DESC, latest.id DESC LIMIT 1)')
        sql = re.sub(r'LEFT JOIN LATERAL\s*\(.*?\) lr ON TRUE', '', sql, flags=re.S)
    sql = sql.replace('::int', '').replace(' ILIKE ', ' LIKE ')
    sql = sql.replace("now() - interval '1 minute'", "datetime('now', '-1 minute')")
    sql = sql.replace("(current_date + interval '30 days')", "date('now', '+30 days')")
    if 'SELECT DISTINCT ON (pv.policy_id)' in sql:
        sql = sql.replace('SELECT DISTINCT ON (pv.policy_id)', 'SELECT')
        sql = sql.replace('FROM policy_versions pv\n',
            'FROM (SELECT *, row_number() OVER (PARTITION BY policy_id ORDER BY created_at DESC, id DESC) AS rn FROM policy_versions) pv WHERE pv.rn = 1\n')
    return sql


DATE_KEYS = {'created_at', 'updated_at', 'resolved_at', 'last_activity',
             'last_read_at', 'last_reply_at', 'effective_date', 'review_date'}


def converted(row):
    if row is None:
        return None
    result = dict(row)
    for key in DATE_KEYS & result.keys():
        if isinstance(result[key], str):
            result[key] = datetime.fromisoformat(result[key])
    return result


class MappingResult:
    def __init__(self, result):
        self.result = result

    def all(self):
        return [converted(row) for row in self.result.all()]

    def first(self):
        return converted(self.result.first())

    def one(self):
        return converted(self.result.one())


class TextResult:
    def __init__(self, result):
        self.result = result

    def mappings(self):
        return MappingResult(self.result.mappings())

    def __getattr__(self, name):
        return getattr(self.result, name)


class OfflineSession(Session):
    def execute(self, statement, params=None, **kwargs):
        # Search ranking is PostgreSQL-only. An empty library result exercises
        # /ask's triage path without claiming to verify pg_trgm offline.
        if isinstance(statement, TextClause) and 'extensions.word_similarity' in str(statement):
            return TextResult(super().execute(text('SELECT 1 WHERE 0')))
        result = super().execute(statement, params, **kwargs)
        return TextResult(result) if isinstance(statement, TextClause) else result


@event.listens_for(OfflineSession, 'before_flush')
def timestamps(session, *_):
    for obj in session.new:
        for key in ('created_at', 'updated_at'):
            if hasattr(obj, key) and getattr(obj, key) is None:
                setattr(obj, key, datetime.now(timezone.utc))


def isolated_database():
    from database import Base
    from models import Department, Role, User, Policy, PolicyVersion

    engine = create_engine('sqlite://', poolclass=StaticPool,
                           connect_args={'check_same_thread': False})

    @event.listens_for(engine, 'connect')
    def functions(connection, _):
        connection.create_function('now', 0, lambda: datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f'))
        connection.create_function('to_timestamp', 1, lambda _: '1970-01-01 00:00:00.000000')
        connection.execute('PRAGMA foreign_keys=ON')

    @event.listens_for(engine, 'before_cursor_execute', retval=True)
    def adapt(connection, cursor, statement, parameters, context, executemany):
        return translate(statement), parameters

    Base.metadata.create_all(engine)
    with OfflineSession(engine) as db:
        db.add_all([Department(id=i, name='Fixture department '+str(i)) for i in range(1, 8)])
        db.add_all([Role(id=1, name='Employee'), Role(id=2, name='Policy Owner'), Role(id=3, name='System Administrator')])
        db.flush()
        names = [('Dana','Brooks',3),('Lucy','Chen',3),('Tom','Bennett',1),
                 ('Maya','Patel',2),('Elena','Rodriguez',1),('Alex','Chen',1),
                 ('Chris','Tanaka',2),('Sam','Okonkwo',1),('Jordan','Rivera',2),
                 ('Gabrielle','Fontaine',2),('Marcus','Webb',2),('Rachel','Sampson',2)]
        db.add_all([User(id=i, first_name=first, last_name=last,
                        email='fixture%d@example.invalid'%i, department_id=1,
                        role_id=rid) for i,(first,last,rid) in enumerate(names,1)])
        db.flush()
        db.add_all([Policy(id=1, title='Unrelated fixture policy', owner_id=12, status='approved'),
                    Policy(id=48, title='Employee Leave', owner_id=9, status='approved')])
        db.flush()
        db.add_all([PolicyVersion(policy_id=i, title='Fixture policy', body='Fixture body', version_no='1.0') for i in (1,48)])
        db.commit()
    return engine, sessionmaker(class_=OfflineSession)
