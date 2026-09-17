"""Database connection and session management for DeRexi: Policy Pilot.

The backend connects to Supabase Postgres directly with the project's
connection string (service role / direct connection), so Row Level Security
does not block backend operations. RLS remains enabled for any future
client-side access.

Set DATABASE_URL in backend/.env (see backend/.env.example).
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load backend/.env regardless of the directory uvicorn is launched from.
load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set.\n"
        "Copy backend/.env.example to backend/.env and paste your Supabase "
        "connection string into it."
    )

# pool_pre_ping avoids stale connections when Supabase recycles them.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model."""


def get_db():
    """FastAPI dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
