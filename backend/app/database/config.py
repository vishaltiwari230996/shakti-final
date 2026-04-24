"""Database configuration.

Reads Neon (Postgres) connection details from environment variables.
"""

import os
from dataclasses import dataclass

try:
    # Load backend/.env if present. Silently no-op if python-dotenv isn't installed.
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass


@dataclass(frozen=True)
class DBConfig:
    url: str
    echo: bool
    pool_size: int
    max_overflow: int
    pool_pre_ping: bool


def _build_url() -> str:
    # Preferred: full DATABASE_URL (Neon provides this in the console).
    # Example:
    #   postgresql+psycopg2://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        # Neon's default URL uses the "postgres://" scheme. SQLAlchemy 2.x
        # expects "postgresql://" (optionally with a driver suffix).
        if url.startswith("postgres://"):
            url = "postgresql+psycopg2://" + url[len("postgres://"):]
        elif url.startswith("postgresql://") and "+psycopg2" not in url:
            url = "postgresql+psycopg2://" + url[len("postgresql://"):]
        return url

    # Fallback: local SQLite for offline dev / tests.
    sqlite_path = os.getenv("SQLITE_PATH", "shakti_dev.db")
    return f"sqlite:///{sqlite_path}"


def get_config() -> DBConfig:
    return DBConfig(
        url=_build_url(),
        echo=os.getenv("DB_ECHO", "false").lower() == "true",
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        pool_pre_ping=True,  # Neon idles connections; keep this on.
    )
