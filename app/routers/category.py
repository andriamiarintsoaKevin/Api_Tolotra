from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.controllers import category as category_controller
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/v1/categories",
    tags=["Stock - Catégories"],
    dependencies=[Depends(get_current_user)],  # Protège toutes les routes
)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
):
    """Crée une nouvelle catégorie de produits."""
    return category_controller.create_category(db, category)


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Liste toutes les catégories avec pagination (skip / limit)."""
    return category_controller.get_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    """Récupère une catégorie par son ID. Retourne 404 si introuvable."""
    return category_controller.get_category_by_id(db, category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
):
    """Met à jour une catégorie (mise à jour partielle supportée)."""
    return category_controller.update_category(db, category_id, category_data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    """Supprime une catégorie par son ID."""
    category_controller.delete_category(db, category_id)
    return None
