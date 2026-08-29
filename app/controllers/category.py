from sqlalchemy.orm import Session
from app import models
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.exceptions.stock import (
    CategoryNotFoundException,
    CategoryAlreadyExistsException,
)


# ─── Helpers privés ─────────────────────────────────────────────────────────

def _check_name_unique(db: Session, name: str, exclude_id: int | None = None) -> None:
    """Vérifie l'unicité du nom de catégorie. Exclut l'ID courant lors d'un UPDATE."""
    query = db.query(models.Category).filter(models.Category.name == name)
    if exclude_id is not None:
        query = query.filter(models.Category.id != exclude_id)
    if query.first():
        raise CategoryAlreadyExistsException(name=name)


# ─── CRUD ───────────────────────────────────────────────────────────────────

def create_category(db: Session, category_data: CategoryCreate) -> models.Category:
    """Crée une nouvelle catégorie après vérification d'unicité du nom."""
    _check_name_unique(db, name=category_data.name)
    db_category = models.Category(**category_data.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[models.Category]:
    """Retourne la liste paginée des catégories."""
    return db.query(models.Category).offset(skip).limit(limit).all()


def get_category_by_id(db: Session, category_id: int) -> models.Category:
    """Récupère une catégorie par son ID. Lève 404 si introuvable."""
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise CategoryNotFoundException(category_id=category_id)
    return category


def update_category(
    db: Session, category_id: int, category_data: CategoryUpdate
) -> models.Category:
    """Met à jour partiellement une catégorie (uniquement les champs fournis)."""
    db_category = get_category_by_id(db, category_id)

    if category_data.name is not None:
        _check_name_unique(db, name=category_data.name, exclude_id=category_id)

    # exclude_unset=True : applique uniquement les champs envoyés par le client
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """Supprime une catégorie (cascade sur les produits définie au niveau du modèle)."""
    db_category = get_category_by_id(db, category_id)
    db.delete(db_category)
    db.commit()
    return True
