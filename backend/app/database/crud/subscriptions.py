"""Subscription CRUD."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Subscription, User
from app.database.models.subscription import BillingCycle, SubscriptionStatus
from app.database.schemas.subscription import SubscriptionCreate, SubscriptionUpdate


def _default_period_end(cycle: BillingCycle) -> Optional[datetime]:
    now = datetime.now(timezone.utc)
    if cycle == BillingCycle.monthly:
        return now + timedelta(days=30)
    if cycle == BillingCycle.yearly:
        return now + timedelta(days=365)
    return None  # lifetime


def get(db: Session, sub_id: UUID | str) -> Optional[Subscription]:
    return db.get(Subscription, sub_id)


def get_active_for_user(db: Session, user_uid: UUID | str) -> Optional[Subscription]:
    return db.execute(
        select(Subscription)
        .where(Subscription.user_uid == user_uid)
        .where(Subscription.status.in_([SubscriptionStatus.active, SubscriptionStatus.trialing]))
        .order_by(Subscription.started_at.desc())
    ).scalars().first()


def create(db: Session, data: SubscriptionCreate) -> Subscription:
    period_end = data.current_period_end or _default_period_end(data.billing_cycle)
    sub = Subscription(
        user_uid=data.user_uid,
        plan_id=data.plan_id,
        billing_cycle=data.billing_cycle,
        auto_renew=data.auto_renew,
        current_period_end=period_end,
        external_customer_id=data.external_customer_id,
        external_subscription_id=data.external_subscription_id,
    )
    db.add(sub)

    # Mirror current plan onto the user row for fast lookups.
    user = db.get(User, data.user_uid)
    if user is not None:
        user.plan_id = data.plan_id

    db.commit()
    db.refresh(sub)
    return sub


def update(db: Session, sub_id: UUID | str, data: SubscriptionUpdate) -> Optional[Subscription]:
    sub = db.get(Subscription, sub_id)
    if sub is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sub, field, value)
    db.commit()
    db.refresh(sub)
    return sub


def cancel(db: Session, sub_id: UUID | str) -> Optional[Subscription]:
    sub = db.get(Subscription, sub_id)
    if sub is None:
        return None
    sub.status = SubscriptionStatus.cancelled
    sub.auto_renew = False
    sub.cancelled_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(sub)
    return sub
