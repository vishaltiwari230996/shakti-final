"""Subscription — a user's purchased plan instance with renewal tracking."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.types import GUID, new_uuid

if TYPE_CHECKING:
    from app.database.models.plan import Plan
    from app.database.models.user import User


class SubscriptionStatus(str, enum.Enum):
    trialing = "trialing"
    active = "active"
    past_due = "past_due"
    cancelled = "cancelled"
    expired = "expired"


class BillingCycle(str, enum.Enum):
    monthly = "monthly"
    yearly = "yearly"
    lifetime = "lifetime"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    user_uid: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.uid", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, name="subscription_status"),
        default=SubscriptionStatus.active,
        nullable=False,
        index=True,
    )
    billing_cycle: Mapped[BillingCycle] = mapped_column(
        Enum(BillingCycle, name="billing_cycle"),
        default=BillingCycle.monthly,
        nullable=False,
    )
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    current_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Renewal date = current_period_end.
    current_period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # External payment provider references (kept provider-agnostic).
    external_customer_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    external_subscription_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)

    user: Mapped["User"] = relationship(back_populates="subscriptions")
    plan: Mapped["Plan"] = relationship(back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription user={self.user_uid} plan={self.plan_id} status={self.status}>"
