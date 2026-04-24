from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CatalogueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_uid: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
