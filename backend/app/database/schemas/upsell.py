from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.database.models.upsell import OfferOutcome, OfferType


class UpsellCreate(BaseModel):
    user_uid: UUID
    offer_type: OfferType
    offer_name: str
    target_plan_id: Optional[UUID] = None
    revenue_amount: Optional[Decimal] = None
    currency: str = "INR"
    notes: Optional[str] = None


class UpsellUpdate(BaseModel):
    outcome: Optional[OfferOutcome] = None
    responded_at: Optional[datetime] = None
    revenue_amount: Optional[Decimal] = None
    notes: Optional[str] = None


class UpsellRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_uid: UUID
    offer_type: OfferType
    offer_name: str
    target_plan_id: Optional[UUID]
    outcome: OfferOutcome
    shown_at: datetime
    responded_at: Optional[datetime]
    revenue_amount: Optional[Decimal]
    currency: str
    notes: Optional[str]
