"""User model. `uid` is the single UUID PK that links every per-user record."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.types import GUID, new_uuid

if TYPE_CHECKING:
    from app.database.models.catalogue import Catalogue
    from app.database.models.plan import Plan
    from app.database.models.subscription import Subscription
    from app.database.models.upsell import UpsellCrossSell


class User(Base):
    __tablename__ = "users"

    # uid is THE key. Everything per-user links to it.
    uid: Mapped[str] = mapped_column(GUID(), primary_key=True, default=new_uuid)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)

    # Hashed password (nullable so Google OAuth users can exist without one).
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Current plan (denormalized convenience pointer; authoritative plan lives in Subscription).
    plan_id: Mapped[Optional[str]] = mapped_column(
        GUID(), ForeignKey("plans.id", ondelete="SET NULL"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    plan: Mapped[Optional["Plan"]] = relationship(back_populates="users")
    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    catalogue: Mapped[Optional["Catalogue"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    upsell_offers: Mapped[List["UpsellCrossSell"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<User {self.email} uid={self.uid}>"
