from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AdminUserOverviewRow(BaseModel):
    """One row from the `admin_user_overview` SQL view."""
    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    name: str
    email: str
    phone_number: Optional[str] = None
    plan_name: Optional[str] = None
    subscription_status: Optional[str] = None
    billing_cycle: Optional[str] = None
    plan_renewal_date: Optional[datetime] = None
    auto_renew: Optional[bool] = None

    # Upsell / cross-sell aggregates
    upsell_offers_shown: int = 0
    upsell_offers_accepted: int = 0
    cross_sell_offers_shown: int = 0
    cross_sell_offers_accepted: int = 0
    total_upsell_revenue: Decimal = Decimal("0")

    user_created_at: datetime
