from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=32)


class UserCreate(UserBase):
    plan_name: Optional[str] = None  # resolved to plan_id during create


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    plan_id: Optional[UUID] = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    uid: UUID
    plan_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
