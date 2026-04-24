# Database Layer

All database concerns live in this folder. Nothing in the rest of the backend
should import SQLAlchemy directly — go through `app.database`.

## Engine

- **Production / staging:** Neon (PostgreSQL). Set `DATABASE_URL` to the
  connection string Neon gives you. The layer automatically normalizes the
  `postgres://` scheme to `postgresql+psycopg2://` and keeps `sslmode=require`.
- **Local dev (optional fallback):** If `DATABASE_URL` is unset, a local
  SQLite file (`shakti_dev.db`) is used so you can iterate offline. The
  admin SQL view is Postgres-only and will be skipped on SQLite.

### Required env vars

```
DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
# Optional:
DB_ECHO=false
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

## Folder layout

```
backend/app/database/
├── __init__.py          # Public surface: engine, SessionLocal, get_db, init_db
├── config.py            # Reads env vars, builds DBConfig
├── session.py           # SQLAlchemy engine + SessionLocal + FastAPI get_db
├── base.py              # Declarative Base
├── types.py             # GUID (UUID) + JSON column helpers (cross-dialect)
├── init_db.py           # create_all + seed plans + install admin view
├── models/              # ORM models (one file per concept)
│   ├── plan.py
│   ├── user.py
│   ├── subscription.py
│   ├── catalogue.py
│   ├── product.py
│   ├── keyword_set.py
│   └── upsell.py
├── schemas/             # Pydantic DTOs for each model + admin row
├── crud/                # All read/write operations
│   ├── users.py         # create() auto-provisions catalogue + keyword_set
│   ├── plans.py
│   ├── subscriptions.py
│   ├── catalogues.py
│   ├── products.py
│   ├── keywords.py
│   ├── upsells.py
│   └── admin.py         # user_overview() — admin dashboard query
└── sql/
    └── admin_user_overview.sql
```

## Schema overview

```
Plan ◄─── User (uid, PK) ──► Subscription ──► Plan
                │
                ├──► Catalogue (1:1) ──► Product (N)
                │                    └─► KeywordSet (1:1)
                │                         (short_tail, mid_tail,
                │                          long_tail, brand_keywords)
                └──► UpsellCrossSell (N)
```

- **`User.uid`** (UUID) is the single PK. Every per-user table has
  `user_uid` as an indexed FK to `users.uid` with `ON DELETE CASCADE`, so
  deleting a user removes their catalogue, products, keywords, subscriptions,
  and upsell history in one go.
- Every **User** automatically gets one **Catalogue** + one **KeywordSet**
  (populated with empty keyword buckets) via `crud.users.create` or the
  `provision_user_workspace` helper.

## Usage

### Initialize on app startup

```python
from app.database import init_db

init_db()  # idempotent: create_all + seed default plans + install admin view
```

### FastAPI dependency

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.database.crud import users, products
from app.database.schemas import UserCreate, ProductCreate

@router.post("/users")
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    # Creates User + auto-provisions Catalogue + empty KeywordSet in one call.
    return users.create(db, payload)

@router.post("/users/{user_uid}/products")
def add_product(user_uid: str, payload: ProductCreate, db: Session = Depends(get_db)):
    return products.create_for_user(db, user_uid, payload)
```

### Admin dashboard

```python
from app.database import get_db
from app.database.crud import admin

rows = admin.user_overview(db)   # list[AdminUserOverviewRow]
# Each row: name, email, plan_name, plan_renewal_date, upsell counts, revenue.
```

## Migrations

`init_db()` uses `Base.metadata.create_all` for convenience. For real
schema changes in production, add Alembic:

```bash
cd backend
alembic init app/database/migrations
# then configure alembic.ini sqlalchemy.url = env:DATABASE_URL
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

`alembic` is already listed in `requirements.txt`.
