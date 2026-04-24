"""Product rows inside a user's catalogue. Amazon-oriented schema."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.types import GUID, json_column_type, new_uuid

if TYPE_CHECKING:
    from app.database.models.catalogue import Catalogue


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("catalogue_id", "asin", name="uq_product_catalogue_asin"),
    )

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=new_uuid)

    catalogue_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("catalogues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Denormalized for fast per-user scans; always equals catalogue.user_uid.
    user_uid: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.uid", ondelete="CASCADE"), nullable=False, index=True
    )

    # Mandatory Amazon-related columns
    asin: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    brand: Mapped[str] = mapped_column(String(255), nullable=False, default="", index=True)
    category: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    sub_category: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    # Rich / optional columns
    bullet_points: Mapped[list] = mapped_column(json_column_type(), default=list)
    images: Mapped[list] = mapped_column(json_column_type(), default=list)
    price: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="INR", nullable=False)
    mrp: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), nullable=True)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reviews: Mapped[list] = mapped_column(json_column_type(), default=list)  # structured review data
    bsr: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Best Sellers Rank
    product_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # Arbitrary extra Amazon attributes the user uploads (A+ content, variations, etc).
    extra: Mapped[dict] = mapped_column(json_column_type(), default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    catalogue: Mapped["Catalogue"] = relationship(back_populates="products")

    def __repr__(self) -> str:
        return f"<Product asin={self.asin} user={self.user_uid}>"
