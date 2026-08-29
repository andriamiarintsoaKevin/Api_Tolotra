from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.controllers import product as product_controller
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/v1/products",
    tags=["Stock - Produits"],
    dependencies=[Depends(get_current_user)],  # Protège toutes les routes
)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    """Crée un nouveau produit en stock."""
    return product_controller.create_product(db, product)


@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Liste tous les produits avec pagination (skip / limit)."""
    return product_controller.get_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Récupère un produit par son ID. Retourne 404 si introuvable."""
    return product_controller.get_product_by_id(db, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    """Met à jour un produit (mise à jour partielle supportée)."""
    return product_controller.update_product(db, product_id, product_data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Supprime un produit par son ID."""
    product_controller.delete_product(db, product_id)
    return None
