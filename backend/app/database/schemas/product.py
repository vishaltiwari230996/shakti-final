from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    asin: str = Field(..., max_length=20)
    product_name: str = Field(..., max_length=512)
    title: str = ""
    description: str = ""
    brand: str = ""
    category: str = ""
    sub_category: str = ""
    bullet_points: List[str] = []
    images: List[str] = []
    price: Optional[Decimal] = None
    currency: str = "INR"
    mrp: Optional[Decimal] = None
    rating: Optional[Decimal] = None
    reviews_count: int = 0
    reviews: list = []
    bsr: Optional[int] = None
    product_url: Optional[str] = None
    extra: dict = {}


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    bullet_points: Optional[List[str]] = None
    images: Optional[List[str]] = None
    price: Optional[Decimal] = None
    mrp: Optional[Decimal] = None
    rating: Optional[Decimal] = None
    reviews_count: Optional[int] = None
    reviews: Optional[list] = None
    bsr: Optional[int] = None
    product_url: Optional[str] = None
    extra: Optional[dict] = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    catalogue_id: UUID
    user_uid: UUID
    created_at: datetime
    updated_at: datetime
