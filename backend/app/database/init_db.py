"""Initialization helpers.

- `init_db()`   — create all tables, seed default plans, create admin view.
- `provision_user_workspace()` — ensure Catalogue + KeywordSet exist for a user
  (called by `crud.users.create`; exposed here for manual re-provisioning).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.base import Base
from app.database.crud import catalogues as catalogues_crud
from app.database.crud import plans as plans_crud
from app.database.models import Catalogue  # noqa: F401 -- ensure model import
from app.database.models import KeywordSet  # noqa: F401
from app.database.models import Plan  # noqa: F401
from app.database.models import Product  # noqa: F401
from app.database.models import Subscription  # noqa: F401
from app.database.models import UpsellCrossSell  # noqa: F401
from app.database.models import User  # noqa: F401
from app.database.schemas.plan import PlanCreate
from app.database.session import SessionLocal, engine

_DEFAULT_PLANS = [
    PlanCreate(
        name="Free",
        description="Starter tier for evaluation.",
        price_monthly=Decimal("0"),
        price_yearly=Decimal("0"),
        features={"catalogue_size": 10, "ai_optimizations_per_month": 25},
    ),
    PlanCreate(
        name="Starter",
        description="For small Amazon sellers.",
        price_monthly=Decimal("1499"),
        price_yearly=Decimal("14990"),
        features={"catalogue_size": 250, "ai_optimizations_per_month": 500},
    ),
    PlanCreate(
        name="Pro",
        description="For growing brands.",
        price_monthly=Decimal("4999"),
        price_yearly=Decimal("49990"),
        features={"catalogue_size": 2500, "ai_optimizations_per_month": 5000, "priority_support": True},
    ),
    PlanCreate(
        name="Enterprise",
        description="Custom — contact sales.",
        price_monthly=Decimal("0"),
        price_yearly=Decimal("0"),
        features={"catalogue_size": -1, "ai_optimizations_per_month": -1, "sso": True, "sla": True},
    ),
]


def _apply_admin_view(db: Session) -> None:
    """Create (or replace) the `admin_user_overview` view. Postgres only."""
    if not engine.url.get_backend_name().startswith("postgres"):
        return  # SQLite dev: skip silently.
    sql_path = Path(__file__).parent / "sql" / "admin_user_overview.sql"
    if not sql_path.exists():
        return
    db.execute(text(sql_path.read_text(encoding="utf-8")))
    db.commit()


def _apply_light_migrations(db: Session) -> None:
    """Tiny additive migrations for dev use — idempotent ALTER IF NOT EXISTS.

    Use Alembic once schema churn stabilizes; this is only to keep dev
    iteration smooth while the model is still moving.
    """
    if not engine.url.get_backend_name().startswith("postgres"):
        return
    statements = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)",
    ]
    for stmt in statements:
        db.execute(text(stmt))
    db.commit()


def init_db(seed_plans: bool = True, create_view: bool = True) -> None:
    """Create all tables, seed default plans, and (on Postgres) create admin view.

    Idempotent — safe to call on every app start during early development.
    For production use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        _apply_light_migrations(db)
        if seed_plans:
            for plan in _DEFAULT_PLANS:
                plans_crud.upsert_by_name(db, plan)
        if create_view:
            _apply_admin_view(db)


def provision_user_workspace(db: Session, user_uid: UUID | str, catalogue_name: Optional[str] = None) -> None:
    """Ensure the per-user Catalogue + KeywordSet exist. Idempotent."""
    catalogues_crud.ensure_for_user(db, user_uid, name=catalogue_name or "My Catalogue")
