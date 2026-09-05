from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.product import ProductCreate, ProductUpdate
from app.schemas.stock_movement import MovementType as MovementTypeSchema, StockMovementCreate


def _get_category_or_404(db: Session, category_id: int) -> models.Category:
    stmt = select(models.Category).where(models.Category.id == category_id)
    category = db.scalar(stmt)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")
    return category


def _get_product_or_404(db: Session, product_id: int) -> models.Product:
    stmt = select(models.Product).where(models.Product.id == product_id)
    product = db.scalar(stmt)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produit introuvable")
    return product


def create_category(db: Session, category_data: CategoryCreate) -> models.Category:
    existing = db.scalar(select(models.Category).where(models.Category.name == category_data.name))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"La catégorie '{category_data.name}' existe déjà")
    category = models.Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> Sequence[models.Category]:
    stmt = select(models.Category).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def get_category_by_id(db: Session, category_id: int) -> models.Category:
    return _get_category_or_404(db, category_id)


def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> models.Category:
    category = _get_category_or_404(db, category_id)
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = _get_category_or_404(db, category_id)
    db.delete(category)
    db.commit()


def create_product(db: Session, product_data: ProductCreate) -> models.Product:
    _get_category_or_404(db, product_data.category_id)
    product = models.Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sector: str | None = None,
    search: str | None = None,
    low_stock: bool | None = None,
) -> Sequence[models.Product]:
    stmt = select(models.Product)
    if sector:
        stmt = stmt.where(models.Product.sector == sector.lower())
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            (models.Product.name.ilike(pattern))
            | (models.Product.sku.ilike(pattern))
            | (models.Product.batch_number.ilike(pattern))
            | (models.Product.serial_number.ilike(pattern))
        )
    if low_stock is True:
        stmt = stmt.where(models.Product.quantity <= models.Product.reorder_threshold)
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()


def get_product_by_code(db: Session, code: str) -> models.Product:
    stmt = select(models.Product).where(
        (models.Product.sku == code)
        | (models.Product.batch_number == code)
        | (models.Product.serial_number == code)
    )
    product = db.scalar(stmt)
    if not product and code.isdigit():
        stmt_id = select(models.Product).where(models.Product.id == int(code))
        product = db.scalar(stmt_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produit avec le code '{code}' introuvable",
        )
    return product


def get_dashboard_metrics(db: Session) -> dict:
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    in_30_days = now + timedelta(days=30)

    products = db.scalars(select(models.Product)).all()

    total_units = sum(p.quantity for p in products)
    active_references = len(products)
    critical_stock_count = sum(1 for p in products if p.quantity <= p.reorder_threshold)

    expiring_soon_count = 0
    expired_count = 0
    cold_chain_compliant = None
    cold_chain_sample_temp = None

    for p in products:
        if p.expiry_date:
            exp = p.expiry_date if p.expiry_date.tzinfo else p.expiry_date.replace(tzinfo=timezone.utc)
            if exp < now:
                expired_count += 1
            elif exp <= in_30_days:
                expiring_soon_count += 1
        if p.sector == "medical" and p.storage_temperature is not None:
            cold_chain_sample_temp = p.storage_temperature
            cold_chain_compliant = cold_chain_compliant is not False
            if p.storage_temperature < 2.0 or p.storage_temperature > 8.0:
                cold_chain_compliant = False

    return {
        "total_units": total_units,
        "active_references": active_references,
        "critical_stock_count": critical_stock_count,
        "expiring_soon_count": expiring_soon_count,
        "expired_count": expired_count,
        "turnover_rate": None,
        "cold_chain": {
            "status": (
                "NO_DATA"
                if cold_chain_compliant is None
                else "NORMAL" if cold_chain_compliant else "ALERT"
            ),
            "current_temp": cold_chain_sample_temp,
            "target_range": "2°C – 8°C",
            "hub": None,
        },
    }


def get_product_by_id(db: Session, product_id: int) -> models.Product:
    return _get_product_or_404(db, product_id)


def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> models.Product:
    product = _get_product_or_404(db, product_id)
    if product_data.category_id is not None:
        _get_category_or_404(db, product_data.category_id)
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = _get_product_or_404(db, product_id)
    db.delete(product)
    db.commit()


def create_stock_movement(db: Session, movement_data: StockMovementCreate) -> models.StockMovement:
    product = _get_product_or_404(db, movement_data.product_id)
    movement_type = models.MovementType(movement_data.movement_type.value)

    if movement_type == models.MovementType.IN:
        product.quantity += movement_data.quantity
    elif movement_type == models.MovementType.OUT:
        if product.quantity < movement_data.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuffisant")
        product.quantity -= movement_data.quantity

    stock_movement = models.StockMovement(
        product_id=product.id,
        quantity=movement_data.quantity,
        movement_type=movement_type,
        reason=movement_data.reason,
    )
    db.add(stock_movement)
    db.commit()
    db.refresh(stock_movement)
    return stock_movement


def list_stock_movements(
    db: Session,
    product_id: int | None = None,
    movement_type: MovementTypeSchema | None = None,
) -> Sequence[models.StockMovement]:
    stmt = select(models.StockMovement)
    if product_id is not None:
        stmt = stmt.where(models.StockMovement.product_id == product_id)
    if movement_type is not None:
        stmt = stmt.where(models.StockMovement.movement_type == models.MovementType(movement_type.value))
    stmt = stmt.order_by(models.StockMovement.created_at.desc())
    return db.scalars(stmt).all()
