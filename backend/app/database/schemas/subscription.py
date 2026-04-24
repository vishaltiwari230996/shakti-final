from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.database.models.subscription import BillingCycle, SubscriptionStatus


class SubscriptionCreate(BaseModel):
    user_uid: UUID
    plan_id: UUID
    billing_cycle: BillingCycle = BillingCycle.monthly
    auto_renew: bool = True
    current_period_end: Optional[datetime] = None
    external_customer_id: Optional[str] = None
    external_subscription_id: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    status: Optional[SubscriptionStatus] = None
    auto_renew: Optional[bool] = None
    current_period_end: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


class SubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_uid: UUID
    plan_id: UUID
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    auto_renew: bool
    started_at: datetime
    current_period_start: datetime
    current_period_end: Optional[datetime]
    cancelled_at: Optional[datetime]
    external_customer_id: Optional[str]
    external_subscription_id: Optional[str]
