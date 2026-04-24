"""Product CRUD."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Catalogue, Product
from app.database.schemas.product import ProductCreate, ProductUpdate


def get(db: Session, product_id: UUID | str) -> Optional[Product]:
    return db.get(Product, product_id)


def list_for_user(db: Session, user_uid: UUID | str, limit: int = 100, offset: int = 0) -> list[Product]:
    return list(
        db.execute(
            select(Product)
            .where(Product.user_uid == user_uid)
            .limit(limit)
            .offset(offset)
        ).scalars()
    )


def list_for_catalogue(db: Session, catalogue_id: UUID | str) -> list[Product]:
    return list(
        db.execute(select(Product).where(Product.catalogue_id == catalogue_id)).scalars()
    )


def create_for_user(db: Session, user_uid: UUID | str, data: ProductCreate) -> Product:
    catalogue = db.execute(
        select(Catalogue).where(Catalogue.user_uid == user_uid)
    ).scalar_one()

    product = Product(
        catalogue_id=catalogue.id,
        user_uid=user_uid,
        **data.model_dump(),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def bulk_create_for_user(
    db: Session, user_uid: UUID | str, rows: list[ProductCreate]
) -> list[Product]:
    catalogue = db.execute(
        select(Catalogue).where(Catalogue.user_uid == user_uid)
    ).scalar_one()
    products = [
        Product(catalogue_id=catalogue.id, user_uid=user_uid, **row.model_dump())
        for row in rows
    ]
    db.add_all(products)
    db.commit()
    for p in products:
        db.refresh(p)
    return products


def update(db: Session, product_id: UUID | str, data: ProductUpdate) -> Optional[Product]:
    product = db.get(Product, product_id)
    if product is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete(db: Session, product_id: UUID | str) -> bool:
    product = db.get(Product, product_id)
    if product is None:
        return False
    db.delete(product)
    db.commit()
    return True
