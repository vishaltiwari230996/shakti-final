"""SQLAlchemy engine + session factory.

Usage (FastAPI dependency):
    from fastapi import Depends
    from sqlalchemy.orm import Session
    from app.database import get_db

    @router.get("/items")
    def list_items(db: Session = Depends(get_db)):
        ...
"""

from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.database.config import get_config

_cfg = get_config()

_engine_kwargs = {
    "echo": _cfg.echo,
    "pool_pre_ping": _cfg.pool_pre_ping,
    "future": True,
}

# SQLite (dev fallback) does not support pool_size / max_overflow.
if not _cfg.url.startswith("sqlite"):
    _engine_kwargs["pool_size"] = _cfg.pool_size
    _engine_kwargs["max_overflow"] = _cfg.max_overflow

engine = create_engine(_cfg.url, **_engine_kwargs)


# Enforce foreign-key ON DELETE CASCADE for the SQLite dev fallback so
# local behavior matches Neon/Postgres.
if engine.url.get_backend_name() == "sqlite":
    @event.listens_for(engine, "connect")
    def _sqlite_fk_pragma(dbapi_connection, _connection_record):  # pragma: no cover
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
