"""Subscription plans (catalog)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.types import GUID, json_column_type, new_uuid

if TYPE_CHECKING:
    from app.database.models.subscription import Subscription
    from app.database.models.user import User


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(512), default="")
    price_monthly: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    price_yearly: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    features: Mapped[dict] = mapped_column(json_column_type(), default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[List["User"]] = relationship(back_populates="plan")
    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="plan")

    def __repr__(self) -> str:
        return f"<Plan {self.name}>"
