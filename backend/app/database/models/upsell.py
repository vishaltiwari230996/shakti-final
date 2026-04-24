"""Upsell / cross-sell tracking.

Each row is one offer presented to a user. Aggregated by the admin view
to surface upsell/cross-sell performance per user.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.types import GUID, new_uuid

if TYPE_CHECKING:
    from app.database.models.plan import Plan
    from app.database.models.user import User


class OfferType(str, enum.Enum):
    upsell = "upsell"
    cross_sell = "cross_sell"


class OfferOutcome(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    expired = "expired"


class UpsellCrossSell(Base):
    __tablename__ = "upsell_cross_sell"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=new_uuid)

    user_uid: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.uid", ondelete="CASCADE"), nullable=False, index=True
    )

    offer_type: Mapped[OfferType] = mapped_column(
        Enum(OfferType, name="offer_type"), nullable=False, index=True
    )
    offer_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional link to a target plan (e.g. upsell Starter -> Pro).
    target_plan_id: Mapped[Optional[str]] = mapped_column(
        GUID(), ForeignKey("plans.id", ondelete="SET NULL"), nullable=True, index=True
    )

    outcome: Mapped[OfferOutcome] = mapped_column(
        Enum(OfferOutcome, name="offer_outcome"),
        default=OfferOutcome.pending,
        nullable=False,
        index=True,
    )

    shown_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    revenue_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="INR", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    user: Mapped["User"] = relationship(back_populates="upsell_offers")
    target_plan: Mapped[Optional["Plan"]] = relationship()

    def __repr__(self) -> str:
        return f"<{self.offer_type.value} user={self.user_uid} outcome={self.outcome.value}>"
