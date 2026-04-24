"""Catalogue CRUD. The catalogue is auto-provisioned on user create, so
typically only read/update operations are used here."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Catalogue, KeywordSet


def get(db: Session, catalogue_id: UUID | str) -> Optional[Catalogue]:
    return db.get(Catalogue, catalogue_id)


def get_for_user(db: Session, user_uid: UUID | str) -> Optional[Catalogue]:
    return db.execute(
        select(Catalogue).where(Catalogue.user_uid == user_uid)
    ).scalar_one_or_none()


def ensure_for_user(db: Session, user_uid: UUID | str, name: str = "My Catalogue") -> Catalogue:
    """Return the user's catalogue, creating (+KeywordSet) if missing."""
    existing = get_for_user(db, user_uid)
    if existing is not None:
        return existing

    catalogue = Catalogue(user_uid=user_uid, name=name)
    db.add(catalogue)
    db.flush()

    db.add(
        KeywordSet(
            catalogue_id=catalogue.id,
            user_uid=user_uid,
            short_tail=[],
            mid_tail=[],
            long_tail=[],
            brand_keywords=[],
        )
    )
    db.commit()
    db.refresh(catalogue)
    return catalogue


def rename(db: Session, catalogue_id: UUID | str, name: str) -> Optional[Catalogue]:
    cat = db.get(Catalogue, catalogue_id)
    if cat is None:
        return None
    cat.name = name
    db.commit()
    db.refresh(cat)
    return cat
