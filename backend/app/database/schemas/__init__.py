"""Pydantic schemas (DTOs) for the database layer.

Separate from `app/models.py` (which holds LLM / API request shapes) so that
DB concerns stay encapsulated in this package.
"""

from app.database.schemas.user import UserCreate, UserUpdate, UserRead
from app.database.schemas.plan import PlanCreate, PlanRead
from app.database.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionRead,
)
from app.database.schemas.catalogue import CatalogueRead
from app.database.schemas.product import ProductCreate, ProductUpdate, ProductRead
from app.database.schemas.keyword_set import KeywordSetUpdate, KeywordSetRead
from app.database.schemas.upsell import UpsellCreate, UpsellUpdate, UpsellRead
from app.database.schemas.admin import AdminUserOverviewRow

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "PlanCreate",
    "PlanRead",
    "SubscriptionCreate",
    "SubscriptionUpdate",
    "SubscriptionRead",
    "CatalogueRead",
    "ProductCreate",
    "ProductUpdate",
    "ProductRead",
    "KeywordSetUpdate",
    "KeywordSetRead",
    "UpsellCreate",
    "UpsellUpdate",
    "UpsellRead",
    "AdminUserOverviewRow",
]
