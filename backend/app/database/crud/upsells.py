"""Upsell / cross-sell CRUD."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import UpsellCrossSell
from app.database.models.upsell import OfferOutcome
from app.database.schemas.upsell import UpsellCreate, UpsellUpdate


def list_for_user(db: Session, user_uid: UUID | str) -> list[UpsellCrossSell]:
    return list(
        db.execute(
            select(UpsellCrossSell)
            .where(UpsellCrossSell.user_uid == user_uid)
            .order_by(UpsellCrossSell.shown_at.desc())
        ).scalars()
    )


def record_offer(db: Session, data: UpsellCreate) -> UpsellCrossSell:
    row = UpsellCrossSell(**data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_outcome(db: Session, offer_id: UUID | str, data: UpsellUpdate) -> Optional[UpsellCrossSell]:
    row = db.get(UpsellCrossSell, offer_id)
    if row is None:
        return None
    payload = data.model_dump(exclude_unset=True)
    if "outcome" in payload and payload["outcome"] != OfferOutcome.pending and "responded_at" not in payload:
        payload["responded_at"] = datetime.now(timezone.utc)
    for field, value in payload.items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row
