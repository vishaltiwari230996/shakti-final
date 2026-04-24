"""Catalogue — exactly one per user, auto-provisioned on user creation."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.types import GUID, new_uuid

if TYPE_CHECKING:
    from app.database.models.keyword_set import KeywordSet
    from app.database.models.product import Product
    from app.database.models.user import User


class Catalogue(Base):
    __tablename__ = "catalogues"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=new_uuid)

    # One catalogue per user — enforce with unique constraint on user_uid.
    user_uid: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("users.uid", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), default="My Catalogue", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="catalogue")
    products: Mapped[List["Product"]] = relationship(
        back_populates="catalogue", cascade="all, delete-orphan", passive_deletes=True
    )
    keyword_set: Mapped[Optional["KeywordSet"]] = relationship(
        back_populates="catalogue",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Catalogue user={self.user_uid}>"
