from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud import (
    create_product,
    delete_product,
    get_dashboard_metrics,
    get_product_by_code,
    get_product_by_id,
    get_products,
    update_product,
)
from app.database import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(
    prefix="/v1/products",
    tags=["Stock - Produits"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_route(
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    return create_product(db, product)


@router.get("/", response_model=List[ProductResponse])
def get_products_route(
    skip: int = 0,
    limit: int = 100,
    sector: str | None = None,
    search: str | None = None,
    low_stock: bool | None = None,
    db: Session = Depends(get_db),
):
    return get_products(
        db,
        skip=skip,
        limit=limit,
        sector=sector,
        search=search,
        low_stock=low_stock,
    )


@router.get("/dashboard/stats")
def get_dashboard_stats_route(
    db: Session = Depends(get_db),
):
    return get_dashboard_metrics(db)


@router.get("/scan/{code}", response_model=ProductResponse)
def scan_product_route(
    code: str,
    db: Session = Depends(get_db),
):
    return get_product_by_code(db, code)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_route(
    product_id: int,
    db: Session = Depends(get_db),
):
    return get_product_by_id(db, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_route(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    return update_product(db, product_id, product_data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_route(
    product_id: int,
    db: Session = Depends(get_db),
):
    delete_product(db, product_id)
    return None
