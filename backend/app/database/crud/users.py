"""User CRUD. Creating a user auto-provisions their catalogue + keyword set."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Catalogue, KeywordSet, Plan, User
from app.database.schemas.user import UserCreate, UserUpdate


def get(db: Session, uid: UUID | str) -> Optional[User]:
    return db.get(User, uid)


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def list_all(db: Session, limit: int = 100, offset: int = 0) -> list[User]:
    return list(db.execute(select(User).limit(limit).offset(offset)).scalars())


def create(db: Session, data: UserCreate) -> User:
    """Create a user AND auto-provision their Catalogue + KeywordSet."""
    plan_id = None
    if data.plan_name:
        plan = db.execute(select(Plan).where(Plan.name == data.plan_name)).scalar_one_or_none()
        if plan is not None:
            plan_id = plan.id

    user = User(
        name=data.name,
        email=str(data.email),
        phone_number=data.phone_number,
        plan_id=plan_id,
    )
    db.add(user)
    db.flush()  # populate user.uid

    catalogue = Catalogue(user_uid=user.uid, name=f"{data.name}'s Catalogue")
    db.add(catalogue)
    db.flush()

    keyword_set = KeywordSet(
        catalogue_id=catalogue.id,
        user_uid=user.uid,
        short_tail=[],
        mid_tail=[],
        long_tail=[],
        brand_keywords=[],
    )
    db.add(keyword_set)

    db.commit()
    db.refresh(user)
    return user


def update(db: Session, uid: UUID | str, data: UserUpdate) -> Optional[User]:
    user = db.get(User, uid)
    if user is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete(db: Session, uid: UUID | str) -> bool:
    user = db.get(User, uid)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True
