"""KeywordSet — exactly one per catalogue, auto-provisioned.

Stores the four keyword buckets the application cares about:
    - short_tail
    - mid_tail
    - long_tail
    - brand_keywords
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.types import GUID, json_column_type, new_uuid

if TYPE_CHECKING:
    from app.database.models.catalogue import Catalogue


class KeywordSet(Base):
    __tablename__ = "keyword_sets"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=new_uuid)

    catalogue_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("catalogues.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    # Denormalized for quick per-user queries.
    user_uid: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.uid", ondelete="CASCADE"), nullable=False, index=True
    )

    short_tail: Mapped[list] = mapped_column(json_column_type(), default=list, nullable=False)
    mid_tail: Mapped[list] = mapped_column(json_column_type(), default=list, nullable=False)
    long_tail: Mapped[list] = mapped_column(json_column_type(), default=list, nullable=False)
    brand_keywords: Mapped[list] = mapped_column(json_column_type(), default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    catalogue: Mapped["Catalogue"] = relationship(back_populates="keyword_set")

    def __repr__(self) -> str:
        return f"<KeywordSet catalogue={self.catalogue_id}>"
