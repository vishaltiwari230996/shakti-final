"""Plan CRUD."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Plan
from app.database.schemas.plan import PlanCreate


def get(db: Session, plan_id: UUID | str) -> Optional[Plan]:
    return db.get(Plan, plan_id)


def get_by_name(db: Session, name: str) -> Optional[Plan]:
    return db.execute(select(Plan).where(Plan.name == name)).scalar_one_or_none()


def list_active(db: Session) -> list[Plan]:
    return list(db.execute(select(Plan).where(Plan.is_active.is_(True))).scalars())


def create(db: Session, data: PlanCreate) -> Plan:
    plan = Plan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def upsert_by_name(db: Session, data: PlanCreate) -> Plan:
    existing = get_by_name(db, data.name)
    if existing is None:
        return create(db, data)
    for field, value in data.model_dump().items():
        setattr(existing, field, value)
    db.commit()
    db.refresh(existing)
    return existing
