"""ORM models for the Shakti 1.2 database layer.

Linkage (PK = User.uid):

    Plan  ─────────┐
                   │ (catalog of subscription plans)
                   ▼
    User (uid) ──► Subscription ──► Plan
      │
      ├──► Catalogue (1:1, auto-provisioned)
      │         │
      │         ├──► Product    (N, per-row Amazon product data)
      │         └──► KeywordSet (1:1, auto-provisioned)
      │
      └──► UpsellCrossSell (N, offers shown / accepted / revenue)
"""

from app.database.models.plan import Plan
from app.database.models.user import User
from app.database.models.subscription import Subscription, SubscriptionStatus, BillingCycle
from app.database.models.catalogue import Catalogue
from app.database.models.product import Product
from app.database.models.keyword_set import KeywordSet
from app.database.models.upsell import UpsellCrossSell, OfferType, OfferOutcome

__all__ = [
    "Plan",
    "User",
    "Subscription",
    "SubscriptionStatus",
    "BillingCycle",
    "Catalogue",
    "Product",
    "KeywordSet",
    "UpsellCrossSell",
    "OfferType",
    "OfferOutcome",
]
