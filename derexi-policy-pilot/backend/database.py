"""Database connection and session management for DeRexi: Policy Pilot.

The backend connects to Supabase Postgres directly with the project's
connection string (service role / direct connection), so Row Level Security
does not block backend operations. RLS remains enabled for any future
client-side access.

Set DATABASE_URL in backend/.env (see backend/.env.example).
"""

import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

@lru_cache(maxsize=1)
def default_session_factory():
    # Resolve production configuration on demand, never by importing models in
    # an isolated demo/test process.
    load_dotenv(Path(__file__).resolve().parent / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not configured")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def SessionLocal():
    return default_session_factory()()


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model."""


def get_db():
    """FastAPI dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
