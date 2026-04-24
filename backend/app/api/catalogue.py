"""Per-user catalogue routes — list/add products, view/update keyword set."""

from __future__ import annotations

import csv
import hashlib
import io
import re
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.database.crud import catalogues as catalogues_crud
from app.database.crud import keywords as keywords_crud
from app.database.crud import products as products_crud
from app.database.models import User
from app.database.schemas.catalogue import CatalogueRead
from app.database.schemas.keyword_set import KeywordSetRead, KeywordSetUpdate
from app.database.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product_enrichment_service import enrich_amazon_product

router = APIRouter(prefix="/my", tags=["my-catalogue"])

_ASIN_RE = re.compile(r"/(?:dp|gp/product|gp/aw/d|product)/([A-Z0-9]{10})", re.IGNORECASE)


def _extract_asin(url: str) -> Optional[str]:
    if not url:
        return None
    m = _ASIN_RE.search(url)
    if m:
        return m.group(1).upper()
    return None


def _fallback_asin(url: str, name: str) -> str:
    seed = (url or name or "").strip().lower()
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest().upper()
    return ("X" + digest)[:10]


@router.get("/catalogue", response_model=CatalogueRead)
def get_my_catalogue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cat = catalogues_crud.get_for_user(db, current_user.uid)
    if cat is None:
        cat = catalogues_crud.ensure_for_user(db, current_user.uid)
    return cat


@router.get("/products", response_model=list[ProductRead])
def list_my_products(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return products_crud.list_for_user(db, current_user.uid, limit=limit, offset=offset)


@router.post("/products", response_model=ProductRead, status_code=201)
def add_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return products_crud.create_for_user(db, current_user.uid, payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = products_crud.get(db, product_id)
    if product is None or str(product.user_uid) != str(current_user.uid):
        raise HTTPException(status_code=404, detail="Product not found")
    return products_crud.update(db, product_id, payload)


@router.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = products_crud.get(db, product_id)
    if product is None or str(product.user_uid) != str(current_user.uid):
        raise HTTPException(status_code=404, detail="Product not found")
    products_crud.delete(db, product_id)


class CsvUploadResult(BaseModel):
    created: int
    skipped: int
    errors: list[str]
    products: list[ProductRead]


@router.post("/products/upload-csv", response_model=CsvUploadResult)
async def upload_products_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bulk-add products from a CSV with columns: product_url, product_name (and optional asin, brand, category).

    Column names are matched case-insensitively. Aliases: url→product_url, name→product_name.
    ASIN is auto-extracted from Amazon URLs when missing.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1", errors="replace")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV is empty or missing a header row")

    # Normalize header names
    header_map = {h.strip().lower(): h for h in reader.fieldnames}
    aliases = {
        "product_url": ["product_url", "url", "link", "amazon_url"],
        "product_name": ["product_name", "name", "title"],
        "asin": ["asin"],
        "brand": ["brand"],
        "category": ["category"],
    }

    def pick(row: dict, key: str) -> str:
        for alias in aliases[key]:
            if alias in header_map:
                val = row.get(header_map[alias])
                if val:
                    return val.strip()
        return ""

    # Ensure catalogue exists
    catalogues_crud.ensure_for_user(db, current_user.uid)

    rows_to_create: list[ProductCreate] = []
    errors: list[str] = []
    seen_asins: set[str] = set()

    for idx, row in enumerate(reader, start=2):  # row 1 = header
        url = pick(row, "product_url")
        name = pick(row, "product_name")
        asin = pick(row, "asin") or _extract_asin(url) or ""

        if not name and not url:
            continue  # skip blank row
        if not name:
            errors.append(f"Row {idx}: missing product_name")
            continue
        if not asin:
            asin = _fallback_asin(url, name)

        if asin in seen_asins:
            errors.append(f"Row {idx}: duplicate ASIN {asin} in file — skipped")
            continue
        seen_asins.add(asin)

        rows_to_create.append(
            ProductCreate(
                asin=asin,
                product_name=name[:512],
                title=name[:1024],
                brand=pick(row, "brand"),
                category=pick(row, "category"),
                product_url=url or None,
            )
        )

    # Filter out ASINs that already exist for this user
    existing = {
        p.asin for p in products_crud.list_for_user(db, current_user.uid, limit=10_000, offset=0)
    }
    fresh = [r for r in rows_to_create if r.asin not in existing]
    skipped = len(rows_to_create) - len(fresh)

    try:
        created = products_crud.bulk_create_for_user(db, current_user.uid, fresh) if fresh else []
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Bulk insert failed: {exc}")

    return CsvUploadResult(
        created=len(created),
        skipped=skipped,
        errors=errors,
        products=created,
    )


class EnrichResult(BaseModel):
    product: ProductRead
    updated_fields: list[str]


@router.post("/products/{product_id}/enrich", response_model=EnrichResult)
def enrich_product(
    product_id: str,
    force: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Scrape Amazon page for this product and fill missing brand/category/title.

    With `force=true`, overwrites existing values.
    """
    product = products_crud.get(db, product_id)
    if product is None or str(product.user_uid) != str(current_user.uid):
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.product_url:
        raise HTTPException(status_code=400, detail="Product has no URL to scrape")

    try:
        data = enrich_amazon_product(product.product_url)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Scrape failed: {exc}")

    updates: dict = {}
    for field in ("brand", "category", "title"):
        val = (data.get(field) or "").strip()
        if not val:
            continue
        current = (getattr(product, field) or "").strip()
        if force or not current:
            updates[field] = val

    if updates:
        updated = products_crud.update(db, product_id, ProductUpdate(**updates))
    else:
        updated = product

    return EnrichResult(product=updated, updated_fields=list(updates.keys()))


class EnrichAllResult(BaseModel):
    total_candidates: int
    enriched: int
    failed: int
    errors: list[str]


@router.post("/products/enrich-missing", response_model=EnrichAllResult)
def enrich_missing_products(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Scrape and fill brand/category for all products with missing values."""
    all_products = products_crud.list_for_user(db, current_user.uid, limit=10_000, offset=0)
    candidates = [
        p for p in all_products
        if p.product_url and (not (p.brand or "").strip() or not (p.category or "").strip())
    ][:limit]

    enriched = 0
    failed = 0
    errors: list[str] = []

    for p in candidates:
        try:
            data = enrich_amazon_product(p.product_url)
        except Exception as exc:
            failed += 1
            errors.append(f"{p.asin}: {exc}")
            continue

        updates: dict = {}
        for field in ("brand", "category", "title"):
            val = (data.get(field) or "").strip()
            current = (getattr(p, field) or "").strip()
            if val and not current:
                updates[field] = val

        if updates:
            products_crud.update(db, p.id, ProductUpdate(**updates))
            enriched += 1

    return EnrichAllResult(
        total_candidates=len(candidates),
        enriched=enriched,
        failed=failed,
        errors=errors[:20],
    )


@router.get("/keywords", response_model=KeywordSetRead)
def get_my_keywords(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ks = keywords_crud.get_for_user(db, current_user.uid)
    if ks is None:
        cat = catalogues_crud.ensure_for_user(db, current_user.uid)
        ks = keywords_crud.ensure_for_catalogue(db, cat.id)
    return ks


@router.put("/keywords", response_model=KeywordSetRead)
def update_my_keywords(
    payload: KeywordSetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ks = keywords_crud.update_for_user(db, current_user.uid, payload)
    if ks is None:
        raise HTTPException(status_code=404, detail="No keyword set found for user")
    return ks
