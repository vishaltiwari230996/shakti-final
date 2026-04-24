"""KeywordSet CRUD."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Catalogue, KeywordSet
from app.database.schemas.keyword_set import KeywordSetUpdate


def get_for_user(db: Session, user_uid: UUID | str) -> Optional[KeywordSet]:
    return db.execute(
        select(KeywordSet).where(KeywordSet.user_uid == user_uid)
    ).scalar_one_or_none()


def get_for_catalogue(db: Session, catalogue_id: UUID | str) -> Optional[KeywordSet]:
    return db.execute(
        select(KeywordSet).where(KeywordSet.catalogue_id == catalogue_id)
    ).scalar_one_or_none()


def ensure_for_catalogue(db: Session, catalogue_id: UUID | str) -> KeywordSet:
    existing = get_for_catalogue(db, catalogue_id)
    if existing is not None:
        return existing
    cat = db.get(Catalogue, catalogue_id)
    if cat is None:
        raise ValueError(f"No catalogue {catalogue_id}")
    ks = KeywordSet(
        catalogue_id=catalogue_id,
        user_uid=cat.user_uid,
        short_tail=[],
        mid_tail=[],
        long_tail=[],
        brand_keywords=[],
    )
    db.add(ks)
    db.commit()
    db.refresh(ks)
    return ks


def update_for_user(db: Session, user_uid: UUID | str, data: KeywordSetUpdate) -> Optional[KeywordSet]:
    ks = get_for_user(db, user_uid)
    if ks is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ks, field, value)
    db.commit()
    db.refresh(ks)
    return ks
