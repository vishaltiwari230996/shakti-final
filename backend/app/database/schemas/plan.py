from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlanBase(BaseModel):
    name: str = Field(..., max_length=64)
    description: str = ""
    price_monthly: Decimal = Decimal("0")
    price_yearly: Decimal = Decimal("0")
    currency: str = "INR"
    features: dict = {}
    is_active: bool = True


class PlanCreate(PlanBase):
    pass


class PlanRead(PlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
