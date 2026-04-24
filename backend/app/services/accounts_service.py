"""Account authentication service — bcrypt password hashing + JWT issue/verify."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import bcrypt
import jwt

# Secret for JWT signing. Falls back to a dev default — override in .env for real use.
_JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-me-in-production")
_JWT_ALGO = "HS256"
_JWT_TTL_HOURS = int(os.getenv("JWT_TTL_HOURS", "168"))  # 7 days


def hash_password(password: str) -> str:
    # bcrypt has a hard 72-byte limit; truncate safely.
    pwd_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        pwd_bytes = password.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, password_hash.encode("utf-8"))
    except Exception:
        return False


def issue_token(user_uid: UUID | str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_uid),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=_JWT_TTL_HOURS)).timestamp()),
        "typ": "access",
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGO)


def decode_token(token: str) -> Optional[str]:
    """Return the user_uid (str) encoded in the token, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGO])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
