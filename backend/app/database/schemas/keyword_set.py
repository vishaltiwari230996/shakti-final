from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class KeywordSetUpdate(BaseModel):
    short_tail: Optional[List[str]] = None
    mid_tail: Optional[List[str]] = None
    long_tail: Optional[List[str]] = None
    brand_keywords: Optional[List[str]] = None


class KeywordSetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    catalogue_id: UUID
    user_uid: UUID
    short_tail: List[str]
    mid_tail: List[str]
    long_tail: List[str]
    brand_keywords: List[str]
    created_at: datetime
    updated_at: datetime
