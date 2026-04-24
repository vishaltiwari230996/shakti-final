"""Database layer for Shakti 1.2.

All schema, ORM models, session management, CRUD, and DB integration code
lives in this package. The rest of the application should only import from
here when it needs DB access.

Entry points:
    from app.database import get_db, init_db
    from app.database.models import User, Plan, Subscription, Catalogue, Product, KeywordSet, UpsellCrossSell
"""

from app.database.session import engine, SessionLocal, get_db
from app.database.base import Base
from app.database.init_db import init_db, provision_user_workspace

__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "Base",
    "init_db",
    "provision_user_workspace",
]
