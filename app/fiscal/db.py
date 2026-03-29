import os
import re
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def get_sync_database_url() -> str:
    url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ibgpt")
    url = re.sub(r"postgresql\+asyncpg://", "postgresql://", url)
    return url


_engine = None
_SessionLocal = None


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(get_sync_database_url(), pool_pre_ping=True)
        _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    return _engine, _SessionLocal


def get_fiscal_session() -> Generator[Session, None, None]:
    _, SessionLocal = get_engine()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
